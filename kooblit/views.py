#-*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.core.context_processors import csrf
import random

from django.template import RequestContext

# @login_required(login_url='/contact/')
def homepage(request, essai=""):
#    c = {}
 #   c.update(csrf(request))
    r = random.randint(0, 1)
    # if essai:
    #     return render_to_response("homepage2.html",{})
    # else:
    return render_to_response("homepage.html",RequestContext(request))
