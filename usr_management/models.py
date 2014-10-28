#-*- coding: utf-8 -*-
import datetime
import re
import string
import hashlib
from bs4 import BeautifulSoup
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.models import UserManager
from django.utils.functional import cached_property
from kooblit_lib import  utils
from countries import data
from utils import MyFileStorage
mfs = MyFileStorage()
# Model utilisateur

# Settings
from django.conf import settings



class UserKooblit(User):
    # username = models.CharField(max_length=30, unique=True)
    is_confirmed = models.BooleanField(default=False)
    civility = models.CharField(_('Status'), max_length = 20, blank = True)
    birthday = models.DateField(null=True)
    objects = UserManager()
    cagnotte = models.FloatField(default=0, unique=False)
    cagnotte_HT = models.FloatField(default=0, unique=False)
    syntheses = models.ManyToManyField('Syntheses', related_name='syntheses_bought+', blank=True, null=True)
    syntheses_achetees = models.ManyToManyField('Version_Synthese', blank=True, null=True)

    def is_author(self):
        try:
            address = Address.objects.get(user=self)
            print ((address.number, address.street_line1, address.zipcode, address.city, address.country))
            print all((address.number, address.street_line1, address.zipcode, address.city, address.country))
            return all((address.number, address.street_line1, address.zipcode, address.city, address.country))
        except Address.DoesNotExist:
            print "nok"
            return False

    def get_user_infos(self):
        return { "username": self.username,
                 "first_name": self.first_name,
                 "name": self.last_name,
        }

    def get_contact(self):
        return { "email": self.email
        }

    def get_address(self):
        try:
            adresse = Address.objects.get(user=self)
            return {
                "number": adresse.number,
                "street_line1": adresse.street_line1,
                "street_line2": adresse.street_line2,
                "zipcode": adresse.zipcode,
                "city": adresse.city
            }
        except Address.DoesNotExist:
            return {}


class Address(models.Model):
    TYPES_CHOICES = (
        ('HOME', _('Home')),
        ('WORK', _('Work')),
        ('OTHER', _('Other'))
    )

    type = models.CharField(_('Type'), max_length=20, choices = TYPES_CHOICES)
    user = models.ForeignKey('UserKooblit')

    departement = models.CharField(_('Departement'), max_length = 50, blank = True)
    corporation = models.CharField(_('Corporation'), max_length = 100, blank = True)
    building = models.CharField(_('Building'), max_length = 20, blank = True)
    floor = models.CharField(_('Floor'), max_length = 20, blank = True)
    door = models.CharField(_('Door'), max_length = 20, blank = True)
    number = models.CharField(_('Number'), max_length = 30, blank = True)
    street_line1 = models.CharField(_('Address 1'), max_length = 100, blank = True)
    street_line2 = models.CharField(_('Address 2'), max_length = 100, blank = True)
    zipcode = models.CharField(_('ZIP code'), max_length = 5, blank = True)
    city = models.CharField(_('City'), max_length = 100, blank = True)
    state = models.CharField(_('State'), max_length = 100, blank = True)

    # French specifics fields
    cedex = models.CharField(_('CEDEX'), max_length = 100, blank = True)
    
    postal_box = models.CharField(_('Postal box'), max_length = 20, blank = True)
    country = models.CharField(_('Country'), max_length = 100, blank = True, choices = data.COUNTRIES)


class Verification(models.Model):
    """docstring for Verification"""
    verification_id = models.CharField(max_length=240, unique=True,
                                       default=False)
    user = models.ForeignKey('UserKooblit')


class Syntheses(models.Model):
    version = models.IntegerField(default=0)
    _file_html = models.FileField(upload_to="syntheses", storage=mfs)
    user = models.ForeignKey('UserKooblit', related_name='+')
    # livre = models.ForeignKey('Book')
    # title = models.CharField(max_length=240, default=False)
    livre_id = models.CharField(max_length=240, blank=False)
    book_title = models.CharField(max_length=settings.MAX_BOOK_TITLE_LEN, default="", blank=False)
    nb_achat = models.BigIntegerField(default=0)
    note_moyenne = models.BigIntegerField(default=0)
    nbre_notes = models.BigIntegerField(default=0)
    date = models.DateField(null=True, default=datetime.datetime.now)
    prix = models.FloatField(default=0)
    gain = models.FloatField(default=0)
    has_been_published = models.BooleanField(default=True)
    EXTRACT_LIMIT = 200

    class Meta:
        unique_together = (("user","livre_id"),)


    def __unicode__(self):
        return u"".join((self.user.username," ",self.book_title))

    @cached_property
    def contenu(self):
        self._file_html.seek(0)  # We need to be at the beginning of the file
        resume = self._file_html.read()
        if not resume.startswith('<html>'):
            resume = "".join(("<html>", resume, "</html>"))
        return resume


    @classmethod
    def get_filename_0(cls, book_title, username):
        book_title = utils.book_slug(book_title)
        inpart = ''.join((book_title, username))
        part = hashlib.sha1(inpart).hexdigest()
        return ''.join(('/tmp/', part, '_0'))


    @property
    def filename(self):
        book_title = utils.book_slug(self.book_title)
        inpart = ''.join((book_title, self.user.username))
        part = hashlib.sha1(inpart).hexdigest()
        return ''.join(('/tmp/', part, '_', str(self.version)))


    @property
    def nbre_mots(self):
        text = BeautifulSoup(self.contenu).get_text()
        exclude = set(string.punctuation)
        filtered_text = ''.join(ch for ch in text if ch not in exclude)
        return len(filtered_text.split(" "))


    @property
    def extrait(self):
        ''' Return the first paragraph of the Synthese
        '''
        soup = BeautifulSoup(self.contenu)
        first_words = soup.getText().split(' ')[:self.EXTRACT_LIMIT]
        regex =  re.compile('.*?'.join(re.escape(word) for word in first_words[-3:]))
        first_match = soup.find(text=regex)

        for parent in first_match.parentGenerator():
            while parent.next_sibling:
                parent.next_sibling.extract()
        return str(soup)


    @property
    def titre(self):
        from manage_books_synth.models import Book
        return Book.objects.get(id=self.livre_id).title

    def can_be_added_by(self, username):
        if not self.has_been_published:
            raise Exception("Should not be ask for adding in")
        buyer = UserKooblit.objects.get(username=username)
        # A changer si changement de regle sur les versions
        return self.user.username != username and not UserKooblit.objects.filter(username=username,syntheses_achetees__synthese=self)

    def publish(self):
        self.date = datetime.datetime.now()
        try:
            version_synthese = Version_Synthese.objects.get(version=self.version, synthese=self)
            if UserKooblit.objects.filter(syntheses_achetees=version_synthese):
                # Quelqu'un a deja achete la version actuelle: il faut incrementer le numero de version
                self.version += 1
                self.save()
                new_version = Version_Synthese(version=self.version, synthese=self, prix=self.prix)
                new_version.save()
            else:
                # Pas d'incrémentation de version
                version_synthese.update()
        except Version_Synthese.DoesNotExist:
            # Création version 0
            new_version = Version_Synthese(version=self.version, synthese=self, prix=self.prix)
            new_version.save()


class Version_Synthese(models.Model):
    version = models.IntegerField()
    synthese = models.ForeignKey('Syntheses')
    prix = models.FloatField()
    publication_date = models.DateField(null=True, default=datetime.datetime.now)
    gain = models.FloatField(default=0)
    nb_achat = models.BigIntegerField(default=0)
    _file = models.FileField(upload_to="syntheses", storage=mfs)

    class Meta:
        unique_together = (("version","synthese"),)

    def can_be_added_by(self, username):
        buyer = UserKooblit.objects.get(username=username)
        # todo: a changer si changement de regle sur les versions
        return self.synthese.user.username != username and not UserKooblit.objects.filter(username=username,syntheses_achetees=self)

    def update(self):
        if self.synthese.version == self.version:
            self.publication_date = datetime.datetime.now()
            self.prix = self.synthese.prix
            self._file = self.synthese._file_html
            self.save()



class Comments(models.Model):
    user = models.ForeignKey('UserKooblit')
    synthese = models.ForeignKey('Syntheses')
    comment = models.CharField(max_length=2048, default=False)
    date = models.DateField(null=True, default=datetime.datetime.now)


class Demande(models.Model):
    user = models.ForeignKey('UserKooblit')
    book = models.CharField(max_length=240, default=False)


class Reinitialisation(models.Model):
    user = models.ForeignKey('UserKooblit')
    rnd = models.CharField(max_length=42, unique=True)


class Transaction(models.Model):
    """docstring for Verification"""
    remote_id = models.CharField(max_length=64, default=False)
    user_from = models.ForeignKey('UserKooblit', default=False, unique=False)


class Entree(models.Model):
    user_dest = models.ForeignKey('UserKooblit', default=False, unique=False)
    montant = models.DecimalField(max_digits=6, decimal_places=2, default=False, unique=False)
    transaction = models.ForeignKey('Transaction', default=False)
