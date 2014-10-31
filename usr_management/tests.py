from django.test import TestCase
from usr_management.models import UserKooblit, Syntheses

# Create your tests here.
class Usr_ManagementTestCase(TestCase):
    def test_suppression_des_syntheses_achetees(self):
        """Animals that can speak are correctly identified"""
        coucou = UserKooblit.objects.get(username__iexact='coucou')
        for i in coucou.syntheses_achetees.all():
            coucou.syntheses_achetees.remove(i)
        self.assertEqual(coucou.syntheses_achetees.all(),[])
