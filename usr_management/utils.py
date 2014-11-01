#-*- coding: utf-8 -*-
import os
import string
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from bs4 import BeautifulSoup, NavigableString

class MyFileStorage(FileSystemStorage):
    # This method is actually defined in Storage
    def get_available_name(self, name):
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name # simply returns the name passed

import shutil
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
# Messages
from django.contrib import messages

PUNC_EXCLUDE = set(string.punctuation + '\n\r')
MAX_CHAR_PAGES = 200

def count_words(text):
    count = 0
    if not text or text in PUNC_EXCLUDE:
        return 0
    if isinstance(text, NavigableString):
        filtered_text = ''.join(ch for ch in text if ch not in PUNC_EXCLUDE)
        return len([i for i in filtered_text.split(' ') if i])
    else:
        t = text.get_text()
        filtered_text = ''.join(ch for ch in t if ch not in PUNC_EXCLUDE)
        return len([i for i in filtered_text.split(' ') if i])
      #  for child in text.contents:
       #     count += count_words(child)
        #return count


def is_empty(t):

    if not isinstance(t, NavigableString) and not isinstance(t, basestring)  and not isinstance(t, unicode):
        if t.name in  ["img"]:
            return False
        text = t.get_text()
    else:
        text = t
    filtered_text = ''.join(ch for ch in text if ch not in PUNC_EXCLUDE)
    return not len([i for i in filtered_text.split(' ') if i])

def pop(text):
    while len(text.contents) == 1 and not isinstance(text.contents[0], NavigableString):
        text = text.contents[0]
    return text


def clean_DOM(text, instance=0):
    if isinstance(text, NavigableString):
        return text

        text2 = pop(text)
        if text2 == text and len(text.contents) == 1:
            return text

        text = text2

    while True:
        for c in text.contents:
            if is_empty(c):
                c.extract()
        for c in text.contents:
            clean_DOM(c, instance+1)

        text2 = pop(text)
        if text2 == text:
            return text
        text = text2

    return text


def try_to_split(text):
    # text = clean_DOM(text)
    if len(text.contents) <= 1:
        return text
    else:
        contents = text.contents
        first = contents[0]
        text.replace_with(first)
        for c in contents[1:]:
            first.insert_after(c)
            first = c
        return first



def find_biggest_child(text):
    n_biggest = 0
    c_biggest = None
    for c in text.contents:
        n = count_words(c)
        if n > n_biggest:
            n_biggest = n
            c_biggest = c

    return c_biggest


def read_pages(text, max_pages=0, clean_page=False):
    current_length = 0
    pages = []
    page = ["<div class='page'>"]


#    text = clean_DOM(text)
    
    for child in text.contents:
        current_length += count_words(child)
        page.append(str(child))
        if current_length >= MAX_CHAR_PAGES:
            page.extend(["</div>"])
            pages.append("".join(page))
            if max_pages and len(pages) >= max_pages:
                break
            else:
                current_length = 0
                page = ["<div class='page'>"]
    if current_length:
        page.extend(["</div>"])
        pages.append("".join(page))

    return pages


def author_required(function):
    def wrap(request, *args, **kwargs):
        from models import UserKooblit
        user = UserKooblit.objects.get(username=request.user.username)
        if user.is_author():
            return function(request, *args, **kwargs)
        else:
            messages.warning(request, "Vous devez compléter vos coordonnées avant de pouvoir écrire une synthèse")
            new_path=reverse('usr_management:dashboard')
            new_path += '?loc=required&next='+request.path
            response = HttpResponseRedirect(new_path, request)
            response['location']+='?loc=required&next='+request.path
            return HttpResponseRedirect(new_path, request)

    return wrap


def ajout_userkooblit_syntheses_achetees():
    import models
    for usr in models.UserKooblit.objects.filter():
        for synth in usr.syntheses.all():
            try:
                version_synth = models.Version_Synthese.objects.get(synthese=synth, version=synth.version)
            except models.Version_Synthese.DoesNotExist:
                version_synth = models.Version_Synthese(
                    synthese=synth, version=synth.version, prix=synth.prix, 
                    gain=synth.gain, nb_achat=synth.nb_achat)
                version_synth.save()
            if version_synth not in usr.syntheses_achetees.all():
                usr.syntheses_achetees.add(version_synth)
                usr.save()

    for synth in models.Syntheses.objects.filter():
        try:
            version_synth = models.Version_Synthese.objects.get(synthese=synth, version=synth.version)
        except models.Version_Synthese.DoesNotExist:
            version_synth = models.Version_Synthese(
                    synthese=synth, version=synth.version, prix=synth.prix, 
                    gain=synth.gain, nb_achat=synth.nb_achat)
            version_synth.save()


def migrate_synth_file():
    import models
    from django.core.files import File
    for synth in models.Syntheses.objects.filter():
        with open(os.path.join(settings.MEDIA_ROOT, synth.filename.replace('/tmp/','syntheses/')), 'r') as f:
            synth._file_html = File(f)
            synth.save()

def migrate_file_version():
    import models
    from django.core.files import File
    for version_synth in models.Version_Synthese.objects.filter():
        filename = version_synth.synthese.filename.replace('_' + str(version_synth.synthese.version), '_' + str(version_synth.version)).replace('/tmp/','syntheses/')
        filename = os.path.join(settings.MEDIA_ROOT, filename)
        with open(filename, 'r') as f:
            version_synth._file = File(f)
            version_synth.save()


def add_title_to_syntheses():
    import models
    from manage_books_synth.models import Book
    for synth in models.Syntheses.objects.filter():
        b = Book.objects.get(id=synth.livre_id)
        synth.book_title = b.title
        synth.save()


def migrate_synth_tmp_file():
    import models
    for synth in models.Syntheses.objects.filter():
        #old_filename = get_name(book_title, synth.user.username)
        old_filename = '/tmp/'+synth._file_html.name
        new_filename = synth.filename
        if os.path.isfile(old_filename):
            shutil.copy2(old_filename, new_filename)
            #os.remove(old_filename)

        old_filename = os.path.join(settings.MEDIA_ROOT, old_filename.replace("/tmp/",'syntheses/'))
        new_filename = os.path.join(settings.MEDIA_ROOT, new_filename.replace("/tmp/",'syntheses/').split('_')[0] + '_0')
        if os.path.isfile(old_filename):
            shutil.copy2(old_filename, new_filename)
            #os.remove(old_filename)
def clean_user_notes():
    import models
    for synth in models.Syntheses.objects.filter():
        synth.nbre_notes = 0
        synth.note_moyenne = 0
        synth.save()

    for user in models.UserKooblit.objects.filter():
        user.syntheses_a_noter.clear()
        for syntheses_achetee in user.syntheses_achetees.all():
            user.syntheses_a_noter.add(syntheses_achetee.synthese)
        user.save()


def migrate():
    clean_user_notes()

def migrate_1():
    ajout_userkooblit_syntheses_achetees()
    add_title_to_syntheses()
    migrate_synth_tmp_file()
    migrate_file_version()
    migrate_synth_file()
