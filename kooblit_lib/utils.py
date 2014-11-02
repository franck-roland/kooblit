from slugify import Slugify
book_slug = Slugify(to_lower=True, separator=' ')


def get_content_for_template(request, syntheses):
    return syntheses
    from usr_management.models import UserKooblit
    if request.user.is_authenticated():
        current_user = UserKooblit.objects.get(username=request.user.username)
    else:
        current_user = None

    bought = []
    can_note = []
    for synth in syntheses:
        bought.append(request.user.is_authenticated() and not synth.can_be_added_by(request.user.username))
        if current_user:
            can_note.append(current_user.can_note(synth))
        else:
            can_note.append(False)
    content = zip(syntheses, bought, can_note)
    return content
