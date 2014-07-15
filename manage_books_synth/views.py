import re

#Settings
from django.conf import settings

#Rendu
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

#search for creation
from search_engine.aws_req import compute_args
from .models import Book, UniqueBook, Recherche


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

    # small_title = StringField(max_length=32, required=True, unique=True)
    # title = StringField(max_length=100, required=True, unique=True)
    # author = ListField(StringField(max_length=100, required=True))
    # description = StringField(max_length=4096, required=False)
    # genres = ListField(ReferenceField(Genre, reverse_delete_rule=NULLIFY))
    # nb_searches = ListField(LongField())
# class UniqueBook(Document):
#     """docstring for UniqueBook"""
#     book = ReferenceField(Book)
#     isbn = StringField(max_length=100, required=True, unique=True)
#     image = URLField()
#     last_update = DateTimeField(default=datetime.datetime.now)

def create_book(book_title):
    connect('docs_db')
    # import pdb;pdb.set_trace()
    s = compute_args(book_title, settings.AMAZON_KEY, exact_match=1, delete_duplicate=0)
    if not s:
        return 1
    first = s[0]
    b = Book(small_title=first[0][:32], title=first[0], author=[first[1]], description=first[4])
    b.save()
    r = Recherche(book=b, nb_searches=1)
    r.save()
    for book_dsc in s:
        u_b = UniqueBook(book=b, isbn=book_dsc[2], image=book_dsc[3])
        u_b.save()

@login_required
def book_search(request, book_title):
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
            # computeEmail(request.user.username,book_title)
            b = Book.objects(title=book_title)
            if not b:
                create_book(book_title)

            return HttpResponseRedirect('/')


def check_exist(request, book_title):
    for b in Book.objects:
        pass

def check_ask(request):
    if request.method == 'POST':
        return HttpResponseRedirect('/')