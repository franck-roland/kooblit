from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import UserManager
from django.utils import timezone
from django.conf import settings
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
    
        