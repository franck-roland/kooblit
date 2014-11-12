# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from usr_management.models import Syntheses
from kooblit_lib.utils import get_content_for_template
import time
import sys

def homepage(request, alt=""):
    if request.method == 'POST':
        print request.POST
    u = {'kooblit_username': request.user.username}
    st = time.clock()
    syntheses = Syntheses.objects.order_by("-date")[:4]
    u['syntheses'] = syntheses
    st = time.clock() - st
    print >> sys.stderr, st
    if alt:
        return render_to_response("alt/homepage.html", RequestContext(request, u))
    else:
        return render_to_response("homepage.html", RequestContext(request, u))


import os
import json
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse

@csrf_exempt
def ipn(request, *args, **kwargs):
    if request.method == 'POST':
        body = request.META.get('wsgi.input').read()
        data = json.loads(input_b.decode('utf­8'))
        signature = request.META.get('HTTP_PAYPLUG_SIGNATURE')
        signature = base64.b64decode(signature)
        k = settings.PAYPLUG_PUBLIC_KEY
        rsa_key = RSA.importKey(k)
        rsa = PKCS1_v1_5.new(rsa_key)
        hash = SHA.new()
        hash.update(body)
        print >> sys.stderr, "inside"
        if rsa.verify(hash, signature):
            message = "IPN received for {first_name} {last_name} for an amount of {amount} EUR"
            message = message.format(first_name=data["first_name"],
            last_name=data["last_name"], amount=data["amount"])
            send_mail("IPN Received", message, settings.DEFAULT_FROM_EMAIL,"franck.l.roland@gmail.com")
        else:
            message = "The signature was invalid."
            send_mail("IPN Failed", message, settings.DEFAULT_FROM_EMAIL,
            "franck.l.roland@gmail.com")
    return HttpResponse()
            
