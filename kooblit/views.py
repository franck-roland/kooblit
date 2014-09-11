# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.core.context_processors import csrf
import random

from django.template import RequestContext


def homepage(request, essai=""):
    u = {'kooblit_username': request.user.username}
    return render_to_response("homepage.html", RequestContext(request, u))
