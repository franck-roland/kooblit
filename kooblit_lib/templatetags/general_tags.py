from django import template
from usr_management.models import UserKooblit, Version_Synthese
register = template.Library()

@register.filter(name='multiply')
def multiply(value, arg):
    return value*arg