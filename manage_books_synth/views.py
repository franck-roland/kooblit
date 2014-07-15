import re

from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse, Http404

# from django.contrib.auth.forms import UserCreationForm
from django.utils.datastructures import MultiValueDictKeyError

from django.contrib.auth.decorators import login_required

from django.template import Context

from django.template import RequestContext

import hashlib

from mongoengine import *
# Emails
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
#User kooblit
from usr_management.models import UserKooblit


from .models import Book

connect('docs_db')

def computeEmail(username, book_title):
    htmly = get_template('email_demande_infos.html')
    email = UserKooblit.objects.get(username=username).email
    d = Context({'username': username, 'book_title': book_title})
    subject, from_email, to = ('[Kooblit] Alerte pour '+book_title, 
                                'noreply@kooblit.com', email)
    html_content = htmly.render(d)
    msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
    msg.content_subtype = "html"
    msg.send()

def book_detail(request, book_title):
    b = Book.objects(title=book_title)
    if not b:
        return render_to_response('doesnotexist.html',RequestContext(request))
    else:
        return render_to_response('details.html',RequestContext(request))

@login_required
def book_search(request, book_title):
    import pdb;pdb.set_trace()
    if request.method == 'GET':
        a = 0
        try:
            refer = request.META['HTTP_REFERER']
            a = re.match("http://"+request.get_host()+'/search/\?.*',refer)
        except KeyError, e:
            return HttpResponseRedirect('/')
            # pass
        except Exception:
            raise

        if a or 1:
            book_title = request.GET['title']
            b = Book.objects(title=book_title)
            if not b:
                return render_to_response('doesnotexist.html',RequestContext(request,{'title': book_title}))
            else:
                return HttpResponseRedirect('../details')
        else:
            return HttpResponseRedirect('/')

    elif request.method == 'POST':
        if request.user.is_authenticated() and request.GET:
            book_title = request.GET['title']
            computeEmail(request.user.username,book_title)
            return HttpResponseRedirect('/')


def check_exist(request, book_title):
    for b in Book.objects:
        pass

def check_ask(request):
    if request.method == 'POST':
        return HttpResponseRedirect('/')

def create_book(book_title):
    pass