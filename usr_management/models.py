import datetime
import re
import string
from bs4 import BeautifulSoup
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.models import UserManager
from django.utils.functional import cached_property

from countries import data
from utils import MyFileStorage
mfs = MyFileStorage()
# Model utilisateur


class UserKooblit(User):
    # username = models.CharField(max_length=30, unique=True)
    is_confirmed = models.BooleanField(default=False)
    civility = models.CharField(_('Status'), max_length = 20, blank = True)
    birthday = models.DateField(null=True)
    # prenom = models.CharField(max_length=30, blank=True)
    # nom = models.CharField(max_length=30, blank=True)
    # norme RFC3696/5321 pour les adresses mail: longueur 254
    # email = models.EmailField(max_length=254, unique=True)
    # User._meta.get_field('email').unique = True
    # password = models.CharField(max_length=64)
    # USERNAME_FIELD = 'username'
    # REQUIRED_FIELDS = ['email']
    objects = UserManager()
    cagnotte = models.DecimalField(max_digits=100, decimal_places=2, default=0, unique=False)
    syntheses = models.ManyToManyField('Syntheses', related_name='syntheses_bought+', blank=True, null=True)


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
    _file = models.FileField(upload_to="syntheses", default=False, storage=mfs)
    _file_html = models.FileField(upload_to="syntheses", default=False, storage=mfs)
    user = models.ForeignKey('UserKooblit', related_name='+')
    # livre = models.ForeignKey('Book')
    # title = models.CharField(max_length=240, default=False)
    livre_id = models.CharField(max_length=240, default=False)
    nb_achat = models.BigIntegerField(default=0)
    note_moyenne = models.BigIntegerField(default=0)
    nbre_notes = models.BigIntegerField(default=0)
    date = models.DateField(null=True, default=datetime.datetime.now)
    prix = models.DecimalField(max_digits=6, decimal_places=2)
    gain = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    has_been_published = models.BooleanField(default=True)
    EXTRACT_LIMIT = 200

    @cached_property
    def contenu(self):
        self._file_html.seek(0)  # We need to be at the beginning of the file
        resume = self._file_html.read()
        if not resume.startswith('<html>'):
            resume = "".join(("<html>", resume, "</html>"))
        return resume

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
        buyer = UserKooblit.objects.get(username=username)
        return self.user.username != username and self not in buyer.syntheses.all()


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
