from django import template
from usr_management.models import UserKooblit
register = template.Library()

@register.filter(name='bought')
def bought(value, user):
    return user.is_authenticated() and not value.can_be_added_by(user.username)

@register.filter(name='can_note')
def can_note(user, synth):
    if not user.is_authenticated():
        return False
    else:
        try:
            current_user = UserKooblit.objects.get(username=user.username)
            return current_user.can_note(synth)
        except UserKooblit.DoesNotExist:
            return False