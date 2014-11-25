# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from usr_management.models import Syntheses
from kooblit_lib.utils import get_content_for_template
from achat.utils import add_to_cart
import time
import sys

@add_to_cart
def homepage(request, alt=""):
    if request.method == 'POST':
        print request.POST
    u = {'kooblit_username': request.user.username}
    st = time.clock()
    # Selection des 4 dernieres synthèses publiées
    syntheses = Syntheses.objects.exclude(has_been_published=False).order_by("-date")[:30]
    u['syntheses'] = syntheses
    st = time.clock() - st
    print >> sys.stderr, st
    if alt:
        return render_to_response("alt/homepage.html", RequestContext(request, u))
    else:
        return render_to_response("homepage.html", RequestContext(request, u))
