# -*- coding: utf-8 -*-
from django.conf import settings
from django.shortcuts import render
from django.shortcuts import render_to_response
from aws_req import compute_args, unsanitize
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
        s = compute_args(title, settings.AMAZON_KEY, escape=1)
        s = [d for d in s if d['book_format'] == u'Broché' or d['book_format'] == 'Hardcover']
        s = [d for d in s if d['language'] == u'Français' or d['language'] == 'Anglais' or d['language'] == 'English']
        for d in s:
            t = urllib.unquote(d['title'])

            if ":" in t:
                t = t.replace(":", ":<span class='book_sub'>")
                t += "</span>"

            d['little_title'] = t + "..."
            d['title'] = unsanitize(d['title'])

        return render_to_response("search_result.html", RequestContext(request, {'title': title, 'resultat': s, 'nb_result': 6}))
    except TypeError as e:
        raise


@login_required
def add_summary(request):
    return HttpResponseRedirect('/')
