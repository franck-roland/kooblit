#-*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.core.context_processors import csrf

def homepage(request, essai=""):
#    c = {}
 #   c.update(csrf(request))
    if essai and essai == "1":
        return render_to_response("homepage2.html",{})
    else:
        return render_to_response("homepage.html",{})
