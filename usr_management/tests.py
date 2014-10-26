from django.test import TestCase
from usr_management.models import UserKooblit, Syntheses

# Create your tests here.
class BuySyntheseTest(object):
    """docstring for BuySyntheseTest"""
    def setUp(self):
        try:
            usr_1 = UserKooblit.objects.get(username="usr_1")
        except UserKooblit.DoesNotExist:
            raise e


