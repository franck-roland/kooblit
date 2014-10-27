# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext


def homepage(request, alt=""):
    u = {'kooblit_username': request.user.username}
    if alt:
        return render_to_response("alt/homepage.html", RequestContext(request, u))    
    else:
        return render_to_response("homepage.html", RequestContext(request, u))
