# -*- coding: utf-8 -*-
import urllib
import json
from aws_req import compute_args, unsanitize, recherche_between_i_and_j
from AmazonRequest import AmazonRequest, ResponseEncoder
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, Http404

def search_view(request):
    title = request.GET.get('title', '')
    if title == '':
        return render_to_response("search_page.html", RequestContext(request))
    # TODO: clean: use str replace
    ch1 = u"àâçéèêëîïôùûüÿ"
    ch2 = u"aaceeeeiiouuuy"
    tmp = []
    for i in title:
        if i in ch1:
            tmp.append(ch2[ch1.index(i)])
        else:
            tmp.append(i)
    title = ''.join(tmp)
    amazon_request = AmazonRequest(title, settings.AMAZON_KEY, escape=True, nb_results_max=6)
    s = amazon_request.compute_args()
    for d in s.results:
        t = urllib.unquote(d['title'])

        if ":" in t:
            t = t.replace(":", ":<span class='book_sub'>", 1)
            t += "</span>"

        d['little_title'] = t + "..."
        d['title'] = unsanitize(d['title'])

    return render_to_response(
        "search_result.html",
        RequestContext(request, {
            'titre': title.title(),
            'resultat': s,
            'nb_result': 6,
            'nb_result_total': len(s)}))


def search_between(request):
    if request.method == "GET":
        begin = int(request.GET["i"])
        end = int(request.GET["j"])
        title = request.GET["title"]
        server_index = int(request.GET["server_index"])
        last_page = int(request.GET["last_page"])

        ch1 = u"àâçéèêëîïôùûüÿ"
        ch2 = u"aaceeeeiiouuuy"
        tmp = []
        for i in title:
            if i in ch1:
                tmp.append(ch2[ch1.index(i)])
            else:
                tmp.append(i)
        title = ''.join(tmp)
        amazon_request = AmazonRequest(title, settings.AMAZON_KEY, escape=True)
        s = amazon_request.recherche_between_i_and_j(begin, end,server_index=server_index, page_nb=last_page)
        for d in s.results:
            t = urllib.unquote(d['title'])

            if ":" in t:
                t = t.replace(":", ":<span class='book_sub'>", 1)
                t += "</span>"

            d['little_title'] = t + "..."
            d['title'] = unsanitize(d['title'])

        return HttpResponse(json.dumps(s, cls=ResponseEncoder), content_type="application/json")
        # return render_to_response(
        #     "row_result.html",
        #     RequestContext(request, {
        #         'titre': title.title(),
        #         'resultat': s,
        #         'nb_result': 6,
        #         'nb_result_total': len(s)}))
