#-*- coding: utf-8 -*-
import datetime
import re
import os
import sys

#URLS
from django.core.urlresolvers import reverse
from django.templatetags.static import static


import hashlib
from bs4 import BeautifulSoup, NavigableString
from django.db import models
# from django.shortcuts import render, render_to_response
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.models import UserManager
from django.utils.functional import cached_property
from kooblit_lib import  utils
from countries import data
from utils import MyFileStorage, count_words, read_pages
from django.utils.encoding import smart_text
from django.core.files import File
# Model utilisateur

# Settings
from django.conf import settings
import random
def random_style():
    style = Synth_Style()
    colors = ["#C3DF9D", "#BCDAE0", "#FC2D6", "#EDC6DF", "#DCBFE4", "#ADB1BA", "#ABB0B7", "#A7AEB4", "#A3ADB0", "#ABB9B4", "#CADBD3", "#DDEBDA", "#EDF7D6", "#F9FCDB", "#FFBC91", "#FF9E91", "#EFA4C5", "#C59BDD", "#B1A1DF", "#AOAEDE", "#97CAD9", "#98DEC4", "#BOEEA3", "#DEF8AA", "#F4FDAD", "#FFF7AE", "#FFECAE", "#FFDCAE", "#FF7D76", "#FAADB0", "#E8AAF5", "#D2AEF5", "#C7BOF5", "#B7B3F6", "#B0C5F5", "#ABDCF4", 
    "#A8F6D2", "#BEFAAB", "#E0FDAD", "#F9FFAE", "#FFF3AF", "#FFFEAAF", "#FFDFAF", "#FFD1AF", "#FF5FAF",]
    style.background_color = colors[int(random.random()*len(colors))%len(colors)]
    fichiers_logos = ['blue', 'green', 'grey', 'marine_blue', 'red', 'violet']
    fichiers_logos = [''.join((settings.PROJECT_ROOT,'/static/img/logo/owl_',i,'.png')) for i in fichiers_logos]
    
    filename = fichiers_logos[int(random.random() * (len(fichiers_logos) - 1) * 10) % len(fichiers_logos)]
    with open(filename,'rb') as f:
        style.logo = File(f)
        style.save()
    
    return style.id


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

    def get_syntheses_achetees_ou_ecrites(self):
        syntheses_versions_achetees = [i[0] for i in self.syntheses_achetees.filter().values_list('synthese')]
        if syntheses_versions_achetees:
            return Syntheses.objects.extra(where=['id IN %s OR user_id=%s'], params=[tuple(syntheses_versions_achetees),self.id]).filter()
        else:
            return Syntheses.objects.filter(user=self)


    def get_syntheses_achetees(self):
        syntheses_versions_achetees = self.syntheses_achetees.filter()
        return Syntheses.objects.filter(version_synthese__in=syntheses_versions_achetees)


    def get_syntheses_a_noter(self):
        syntheses_notees = [i[0] for i in Note.objects.values_list('synthese_id').filter(user=self)]
        syntheses_achetees = [i[0] for i in self.get_syntheses_achetees().values_list('id')]
        if syntheses_notees and syntheses_achetees:
            return Syntheses.objects.extra(where=['id NOT IN %s','id IN %s'], params=[tuple(syntheses_notees),tuple(syntheses_achetees)]).filter()
        elif not syntheses_notees:
            return syntheses_achetees


    def can_note(self, synthese):
        if synthese.user_id == self.id:
            return False
        else:
            syntheses_achetees = self.syntheses_achetees.filter(synthese=synthese)
            return syntheses_achetees and not Note.objects.filter(user=self, synthese=synthese)


    def is_author(self):
        try:
            address = Address.objects.get(user=self)
            return all((address.number, address.street_line1, address.zipcode, address.city, address.country))
        except Address.DoesNotExist:
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

class Synth_Style(models.Model):
    logo_height=models.PositiveIntegerField(default=40)
    logo_width=models.PositiveIntegerField(default=40)
    background_color = models.CharField(default="#53C1AC", unique=False, max_length=32)
    logo = models.ImageField(default='little_owl_grey.png', height_field="logo_height", width_field="logo_width", upload_to="img/kooblit_cards")

    def __unicode__(self):
        return u''.join(('color:',self.background_color,' img:',self.logo.url))

class Syntheses(models.Model):
    style = models.ForeignKey('Synth_Style', default=random_style)
    version = models.IntegerField(default=0)
    _file_html = models.FileField(upload_to="syntheses")
    file_pdf = models.FileField(upload_to="syntheses")
    user = models.ForeignKey('UserKooblit', related_name='+')
    # livre = models.ForeignKey('Book')
    # title = models.CharField(max_length=240, default=False)
    livre_id = models.CharField(max_length=240, blank=False)
    book_title = models.CharField(max_length=settings.MAX_BOOK_TITLE_LEN, default="", blank=False)
    nb_achat = models.BigIntegerField(default=0)
    note_moyenne = models.FloatField(default=0)
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

    @property
    def is_free(self):
        return self.nbre_notes < settings.MIN_NOTE or self.note_moyenne < settings.MIN_MEAN

    @property
    def nb_pages(self):
        if self.file_pdf.name != "0" and self.file_pdf.name:
            import pyPdf
            try:
                reader = pyPdf.PdfFileReader(self.file_pdf)
                nb_pages = reader.getNumPages()
                if nb_pages:
                    return nb_pages
                else:
                    from manage_books_synth.tasks import create_pdf
                    create_pdf(self.user.username, self)
                    return 0
            except Exception, e:
                from manage_books_synth.tasks import create_pdf
                create_pdf(self.user.username, self)
                return 0
        else:
            return 0

    @cached_property
    def titre(self):
        return u"".join(("<h1 id='titre_synthese'>Koob de <span class='book_title'>", self.book_title,
            "</span> par <span class='book_title'><a href=",reverse('users',args=(self.user.username,)),">", self.user.username, "</a></span></h1>"))


    @cached_property
    def contenu(self):
        self._file_html.seek(0)  # We need to be at the beginning of the file
        _title = u"".join(("<h1 id='titre_synthese'>Koob de <span class='book_title'>", self.book_title,
            "</span> par <span class='book_title'>", self.user.username, "</span></h1>"))
        resume = smart_text(self._file_html.read())
        resume = "".join((_title, resume))
        return resume.encode("utf-8")


    @cached_property
    def contenu_sans_titre(self):
        self._file_html.seek(0)  # We need to be at the beginning of the file
        resume = unicode(self._file_html.read(),'utf-8')
        return resume.encode("utf-8")


    def contenu_pdf(self):
        cont = self.contenu
        template_name = os.path.join(settings.TEMPLATE_DIRS[0],'pdf/pdf_render.html')
        with open(template_name,'r') as f:
            head = f.read()
        return "".join((head,cont))

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
        return 0

    @cached_property
    def pages(self):
        s = self.contenu_sans_titre
        s = s.replace("\n","")
        return [s,]
        soup = BeautifulSoup(s)
        body = soup.find("body")
        return read_pages(body)

    @property
    def extrait(self):
        ''' Return the first paragraph of the Synthese
        '''
        if not self.book_title:
            from manage_books_synth.models import Book
            self.book_title = Book.objects.get(id=self.livre_id).title
            self.save()
        contenu_html = self.contenu_sans_titre.replace("><","> <")
        soup = BeautifulSoup(contenu_html)
        body = soup.find("body")
        current_length = 0
        extrait = ["<html>", "<body>"]

        text = body.getText().split(' ')
        if len(text) < self.EXTRACT_LIMIT*3:
            extrait.extend(text[:int(0.3*len(text))])
        else:
            extrait.extend(text[:self.EXTRACT_LIMIT])
        extrait.extend(["...", "</body>", "</html>"])
        return " ".join(extrait)


    def can_be_added_by(self, username):
        buyer = UserKooblit.objects.get(username=username)
        # A changer si changement de regle sur les versions
        return self.has_been_published and self.user.username != username and not UserKooblit.objects.filter(username=username, syntheses_achetees__synthese=self)

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
    _file = models.FileField(upload_to="syntheses")

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


class Note(models.Model):
    user = models.ForeignKey("UserKooblit")
    synthese = models.ForeignKey("Syntheses")
    valeur = models.FloatField()

    class Meta:
        unique_together = (('user', 'synthese'),)

    def __unicode__(self):
        return u''.join((self.user.username, u' pour synthese: ', unicode(str(self.synthese),'utf8')))


class DueNote(models.Model):
    user = models.ForeignKey("UserKooblit")
    synthese = models.ForeignKey("Syntheses")
    date = models.DateTimeField(auto_now_add=True)

    class Meta(object):
        unique_together = (('user', 'synthese'),)



class Comments(models.Model):
    user = models.ForeignKey('UserKooblit')
    synthese = models.ForeignKey('Syntheses')
    comment = models.CharField(max_length=2048, default=False)
    date = models.DateTimeField(auto_now_add=True)


class Demande(models.Model):
    user = models.ForeignKey('UserKooblit')
    book = models.CharField(max_length=240, default=False)


class Reinitialisation(models.Model):
    user = models.ForeignKey('UserKooblit')
    rnd = models.CharField(max_length=42, unique=True)



