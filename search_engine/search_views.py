# -*- coding: utf-8 -*-
from django.conf import settings
from django.shortcuts import render
from django.shortcuts import render_to_response
from aws_req import compute_args
from django.http import HttpResponse
from django.utils.http import urlquote
# Create your views here.
from django.views.decorators.cache import cache_page
from django.http import HttpResponseBadRequest


def search_view(request):
#    import pdb;pdb.set_trace()
    
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
        s = compute_args(title,settings.AMAZON_KEY)
        return render_to_response("search_result.html",{'resultat':s})
    except TypeError as e:
        return HttpResponseBadRequest("Pas de donnees")

