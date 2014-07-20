from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import UserManager
from django.utils import timezone
from django.conf import settings
# from manage_books_synth.models import Book

import datetime
# Model utilisateur

class UserKooblit(User):
    # username = models.CharField(max_length=30, unique=True)
    birthday = models.DateField(null=True)
    is_confirmed = models.BooleanField(default=False)
    # prenom = models.CharField(max_length=30, blank=True)
    # nom = models.CharField(max_length=30, blank=True)
    # norme RFC3696/5321 pour les adresses mail: longueur 254
    # email = models.EmailField(max_length=254, unique=True)
    # User._meta.get_field('email').unique = True
    # password = models.CharField(max_length=64)
    # USERNAME_FIELD = 'username'
    # REQUIRED_FIELDS = ['email']
    objects = UserManager()


class Verification(models.Model):
    """docstring for Verification"""
    verification_id = models.CharField(max_length=240, unique=True, default=False)
    user = models.ForeignKey('UserKooblit')
    
class Syntheses(models.Model):
    _file = models.FileField(upload_to="syntheses")
    _file_html = models.FileField(upload_to="syntheses", default=False)
    user = models.ForeignKey('UserKooblit')
    # livre = models.ForeignKey('Book')
    title = models.CharField(max_length=240, default=False)
    livre_id = models.CharField(max_length=240, default=False)
    nb_achat = models.BigIntegerField(default=0)
    note_moyenne = models.BigIntegerField(default=0)
    nbre_notes = models.BigIntegerField(default=0)
    date = models.DateField(null=True, default=datetime.datetime.now)
    prix = models.DecimalField(max_digits=6, decimal_places=2)


class Comments(models.Model):
    user = models.ForeignKey('UserKooblit')
    synthese = models.ForeignKey('Syntheses')
    comment = models.CharField(max_length=2048, default=False)
    date = models.DateField(null=True, default=datetime.datetime.now)
        
        