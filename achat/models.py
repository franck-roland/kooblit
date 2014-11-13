from django.db import models

class Transaction(models.Model):
    """docstring for Verification"""
    remote_id = models.CharField(max_length=64, default=False)
    user_from = models.ForeignKey('usr_management.UserKooblit', default=False, unique=False)


class Entree(models.Model):
    user_dest = models.ForeignKey('usr_management.UserKooblit', default=False, unique=False)
    synthese_dest = models.ForeignKey('usr_management.Syntheses', default=False, unique=False)
    montant = models.DecimalField(max_digits=6, decimal_places=2, default=False, unique=False)
    transaction = models.ForeignKey('Transaction', default=False)
