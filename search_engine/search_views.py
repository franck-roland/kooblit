# -*- coding: utf-8 -*-
from django.conf import settings
from django.shortcuts import render
from django.shortcuts import render_to_response
from aws_req import compute_args
from aws_req import compute_args2
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.utils.http import urlquote
# Create your views here.
from django.views.decorators.cache import cache_page
from django.http import HttpResponseBadRequest

from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from .models import Book
import urllib
# from mongoengine import *
# connect('docs_db')

def search_view(request):
#    import pdb;pdb.set_trace()
    u = {'kooblit_username': request.user.username}

    title = ""
    try:
        title = request.GET.get('title', '')
        ch1 = u"àâçéèêëîïôùûüÿ"
        ch2 = u"aaceeeeiiouuuy"
        tmp = []
        for i in title:
            if i in ch1:
                tmp.append(ch2[ch1.index(i)])
            else:
                tmp.append(i)
        title = ''.join(tmp)
        # import pdb;pdb.set_trace()
        s = compute_args(title, settings.AMAZON_KEY, escape=1)
        for i,j in enumerate(s):
            s[i].append(urllib.unquote(j[0])[:32])

        return render_to_response("search_result.html", RequestContext(request, {'resultat': s}))
    except TypeError as e:
        raise

@login_required
def add_summary(request):
    return HttpResponseRedirect('/')