from django import template
from usr_management.models import UserKooblit, Version_Synthese
register = template.Library()

@register.filter(name='bought')
def bought(synthese, user):
    if not user.is_authenticated():
        return False
    else:
        try:
            current_user = user.userkooblit
            if synthese.user_id == current_user.id: # Auteur de la synthese
                return True
            if current_user.syntheses_achetees.filter(synthese=synthese): # Dans les achats
                return True
            else:
                return False
        except Exception, e:
            return False


@register.filter(name='can_note')
def can_note(user, synth):
    if not user.is_authenticated():
        return False
    else:
        try:
            return user.userkooblit.can_note(synth)
        except Exception, e:
            return False
