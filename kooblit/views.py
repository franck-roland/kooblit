# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from usr_management.models import Syntheses

def homepage(request, alt=""):
    u = {'kooblit_username': request.user.username}
    if alt:
        content = [(s,0) for s in Syntheses.objects.order_by("-date")[:4]]
        u['content'] = content
        return render_to_response("alt/homepage.html", RequestContext(request, u))
    else:
        return render_to_response("homepage.html", RequestContext(request, u))
