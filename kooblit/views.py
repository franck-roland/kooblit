# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from usr_management.models import Syntheses

from kooblit_lib.utils import get_content_for_template

def homepage(request, alt=""):
    u = {'kooblit_username': request.user.username}
    syntheses = Syntheses.objects.order_by("-date")[:4]
    u['syntheses'] = syntheses
    if alt:
        return render_to_response("alt/homepage.html", RequestContext(request, u))
    else:
        return render_to_response("homepage.html", RequestContext(request, u))
