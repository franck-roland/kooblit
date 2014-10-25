#-*- coding: utf-8 -*-
import os
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
import models

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
            return HttpResponseRedirect('/users/'+user.username, request)

    return wrap