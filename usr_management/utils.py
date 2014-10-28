#-*- coding: utf-8 -*-
import os
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
import models
from django.core.urlresolvers import reverse

# Messages
from django.contrib import messages

class MyFileStorage(FileSystemStorage):
    # This method is actually defined in Storage
    def get_available_name(self, name):
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name # simply returns the name passed

def author_required(function):

    def wrap(request, *args, **kwargs):
        user = models.UserKooblit.objects.get(username=request.user.username)
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
    us = models.UserKooblit.objects.filter()
    for usr in us:
        for synth in usr.syntheses.all():
            try:
                version_synth = models.Version_Synthese.objects.get(synthese=synth, version=synth.version)
            except models.Version_Synthese.DoesNotExist:
                version_synth = models.Version_Synthese(synthese=synth, version=synth.version, prix=synth.prix)
                version_synth.save()
            if version_synth not in usr.syntheses_achetees.all():
                usr.syntheses_achetees.add(version_synth)
                usr.save()
                