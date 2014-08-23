#-*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.core.context_processors import csrf
import random

from django.template import RequestContext

# @login_required(login_url='/contact/')
def homepage(request, essai=""):
#    c = {}
    print request
    try:
        u = {'kooblit_username': request.user.username}
    except Exception, e:
        u = {}
        raise e
    return render_to_response("homepage.html",RequestContext(request, u))
