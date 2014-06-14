#-*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.core.context_processors import csrf
import random

def homepage(request, essai=""):
#    c = {}
 #   c.update(csrf(request))
    r = random.randint(0, 1)
    if r:
        return render_to_response("homepage2.html",{})
    else:
        return render_to_response("homepage.html",{})
