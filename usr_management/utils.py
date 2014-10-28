#-*- coding: utf-8 -*-
import os
from django.core.files.storage import FileSystemStorage
from django.conf import settings

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
        print version_synth.synthese
        print filename
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
        print old_filename
        new_filename = synth.filename
        if os.path.isfile(old_filename):
            shutil.copy2(old_filename, new_filename)
            #os.remove(old_filename)

        old_filename = os.path.join(settings.MEDIA_ROOT, old_filename.replace("/tmp/",'syntheses/'))
        print old_filename
        new_filename = os.path.join(settings.MEDIA_ROOT, new_filename.replace("/tmp/",'syntheses/').split('_')[0] + '_0')
        if os.path.isfile(old_filename):
            print new_filename
            shutil.copy2(old_filename, new_filename)
            #os.remove(old_filename)

def migrate():
    ajout_userkooblit_syntheses_achetees()
    add_title_to_syntheses()
    migrate_synth_tmp_file()
    migrate_file_version()
    migrate_synth_file()
