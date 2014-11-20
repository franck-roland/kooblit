from django import template
from usr_management.models import UserKooblit, Version_Synthese
register = template.Library()

@register.filter(name='bought')
def bought(value, user):
    if not user.is_authenticated():
        return False
    else:
        try:
            current_user = user
            if value.user == current_user: # Auteur de la synthese
                return True
            if Version_Synthese.objects.filter(userkooblit=current_user, synthese=value): # Dans les achats
                return True
            else:
                return False
        except Exception, e:
            return False
    return user.is_authenticated() and not value.can_be_added_by(user.username)

@register.filter(name='can_note')
def can_note(user, synth):
    if not user.is_authenticated():
        return False
    else:
        try:
            return user.can_note(synth)
        except Exception, e:
            return False
