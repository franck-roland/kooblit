# -*- coding: utf-8 -*-
import os
import re
import sys
import datetime
import urllib
import hashlib

#Settings
from django.conf import settings

from django.core.files import File
#Rendu
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse, Http404

# from django.contrib.auth.forms import UserCreationForm
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib.auth.decorators import login_required
from django.template import Context
from django.template import RequestContext


# Emails
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context


#search for creation
from search_engine.aws_req import compute_args
from .models import Book, UniqueBook, Recherche
#Usr_management models
from usr_management.models import UserKooblit, Syntheses

from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from .forms import UploadFileForm

# Imaginary function to handle an uploaded file.
from HTMLParser import HTMLParser


#fichier docx
from docx import opendocx, getdocumentHtml



def check_html(file_name):
    parser = HTMLParser()
    with open(file_name, 'rb') as _f:
        parser.feed(_f.read())

from pyPdf import PdfFileReader
from pyPdf.utils import PdfReadError

def check_pdf(file_name):
    try:
        doc = PdfFileReader(file(file_name, "rb"))
        return 0
    except PdfReadError, e:
        return 1
    except Exception:
        raise
# _file = models.FileField(upload_to="syntheses")
#     user = models.ForeignKey('UserKooblit')
#     livre_id = models.CharField(max_length=240, unique=True, default=False)
#     nb_achat = models.BigIntegerField(default=0)
#     note_moyenne = models.BigIntegerField(default=0)
#     nbre_notes = models.BigIntegerField(default=0)
#     date = models.DateField(null=True, default=datetime.datetime.now)
#     prix = models.DecimalField(max_digits=6, decimal_places=2)
def slugify(filename):
    ch1 = u"àâçéèêëîïôùûüÿ"
    ch2 = u"aaceeeeiiouuuy"
    tmp = []
    for i in filename:
        if i in ch1:
            tmp.append(ch2[ch1.index(i)])
        else:
            tmp.append(i)
    return ''.join(tmp)

def get_name(book_title, title, username):
    inpart = ''.join((book_title, slugify(title), username))
    part = hashlib.sha1(inpart).hexdigest()
    return ''.join(('/tmp/', part))

def create_tmp_file(f, book_title, title, username):
    file_name = get_name(book_title, title, username)
    with open(file_name, 'wb') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    document = opendocx(file_name)
    with open(file_name+'.html', 'w') as newfile:
        paratextlist = getdocumentHtml(document)
        # Make explicit utf-8 version
        newparatextlist = []
        for paratext in paratextlist:
            newparatextlist.append(paratext.encode("utf-8"))
        #Join Paragraphs and print them
        newfile.write(''.join(newparatextlist))

    user = UserKooblit.objects.get(username=username)
    book = Book.objects.get(title=book_title)
    synthese = Syntheses.objects.filter(user=user,title=title,livre_id=book.id)
    return synthese

def create_file(book_title, title, username):
    user = UserKooblit.objects.get(username=username)
    book = Book.objects.get(title=book_title)
    file_name = get_name(book_title, title, username)
    with open(file_name, 'rb') as destination:
        with open(file_name+'.html', 'r') as newfile:
            try:
                synthese = Syntheses.objects.get(user=user, title=title, livre_id=book.id)
                synthese._file = File(destination)
                synthese._file_html = File(newfile)
                synthese.save()
            except Syntheses.DoesNotExist, e: 
                synthese = Syntheses(_file=File(destination), _file_html=File(newfile), 
                title=title, user=user, livre_id=book.id, prix=2)
                synthese.save()
                
    os.remove(file_name)
    os.remove(file_name+'.html')


def delete_tmp_file(book_title, title, username):
    filename = get_name(book_title, title, username)
    if os.path.isfile(filename):
        os.remove(filename)
    if os.path.isfile(filename+'.html'):
        os.remove(filename+'.html')

def create_book(book_title):
    s = compute_args(book_title, settings.AMAZON_KEY, exact_match=1, delete_duplicate=0)
    if not s:
        return 1
    first = s[0]
    book = Book(small_title=first['title'][:32], title=first['title'][:256], 
        author=[first['author']], description=first['summary'])
    book.save()
    r = Recherche(book=book, nb_searches=1)
    r.save()
    isbn_list=[]
    for book_dsc in s:
        try:
            if not book_dsc['isbn'] in isbn_list:
                u_b = UniqueBook(book=book, isbn=book_dsc['isbn'], image=book_dsc['image'])
                u_b.save()
                isbn_list.append(book_dsc['isbn'])
        except Exception, e:
            raise
    return 0

def create_book_if_doesnt_exist(book_title):
    try:
        b = Book.objects.get(title=book_title)
    except Book.DoesNotExist, e:
        create_book(book_title)

@login_required
def upload_file(request, book_title, title):
    book_title = urllib.unquote(book_title)
    ret = {'form': '', 'prev': '', 'error': '', 'replace': ''}
    username = request.user.username
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if request.POST.get('oui',''):
            create_file(book_title, title, username)
            delete_tmp_file(book_title, title, username)
            return HttpResponseRedirect('/')

        elif request.POST.get('oui_replace',''):
            return HttpResponseRedirect(request.POST['title'],RequestContext(request,ret))

        elif request.POST.get('non_replace',''):
            delete_tmp_file(book_title, request.POST['title'], username)
            form = UploadFileForm()
            ret['form'] = form
            return render_to_response('upload.html', RequestContext(request,{'form': form, 'prev': ''}))

        else:
            ret['form'] = form
            if request.POST.get('non',''):
                return render_to_response('upload.html', 
                    RequestContext(request,ret))
            else:
                ret['form'] = form
                if form.is_valid():
                    if create_tmp_file(request.FILES['file'], book_title, request.POST['title'], username):
                        ret['replace'] = 'oui'
                        ret['title'] = urllib.quote(request.POST['title'])
                        return render_to_response('upload.html', RequestContext(request,ret))
                        # ret['error']='Une synthese avec le meme nom existe deja. Voulez-vous la remplacer'
                    return HttpResponseRedirect(urllib.quote(request.POST['title']),RequestContext(request,ret))
    elif title:
        book = Book.objects.get(title=book_title)
        user = UserKooblit.objects.get(username=username)
        file_html = get_name(book_title, title, username)+'.html'
        try:
            with open(file_html, 'r') as f:
                s = f.read()
            ret['prev'] = s
        except IOError:
            raise Http404()
            # form = UploadFileForm()
            # ret['form'] = form
        return render_to_response('upload.html', RequestContext(request,ret))

    else:
        form = UploadFileForm()
        ret['form'] = form
        return render_to_response('upload.html', RequestContext(request,{'form': form, 'prev': ''}))


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

# def book_detail(request, book_title):
#     b = Book.objects(title=book_title)
#     if not b:
#         return render_to_response('doesnotexist.html',RequestContext(request))
#     else:
#         return render_to_response('details.html',RequestContext(request))

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
# import pdb;pdb.set_trace()



@login_required
def book_search(request, book_title):
    book_title = urllib.unquote(book_title)
    if request.method == 'GET':
        try:

            b = Book.objects.get(title=book_title)
            res = Recherche.objects(book=b)[0]

            if datetime.datetime.now().date() != res.day .date():
                res = Recherche(book=b, nb_searches=1)
            else:
                res.nb_searches += 1
            res.save()
            return HttpResponseRedirect('../')
        except Book.DoesNotExist, e:
            return render_to_response('doesnotexist.html',RequestContext(request,{'title': book_title}))

    elif request.method == 'POST':
        if request.user.is_authenticated():
            # book_title = request.GET['title']
            # computeEmail(request.user.username,book_title)
            try:
                b = Book.objects.get(title=book_title)
            except Book.DoesNotExist, e:
                if not create_book(book_title):
                    b = Book.objects.get(title=book_title)
            return HttpResponseRedirect('../')
    else:
        raise Http404()
            
@login_required
def book_detail(request, book_title):
    book = Book.objects.get(title=book_title)
    res = Recherche.objects(book=book)[0]
    if not book:
        return HttpResponseRedirect('/')        
    u_b = UniqueBook.objects(book=book)[0]
    syntheses = Syntheses.objects.filter(livre_id=book.id)
    syntheses = [{'username':i.user.username, 'title':i.title,
     'prix':i.prix, 'date':i.date} for i in syntheses]
    # import pdb;pdb.set_trace()
    return render_to_response('book_details.html',RequestContext(request,{'title': book.title, 'img_url': u_b.image, 
        'nb_searches': res.nb_searches, 'syntheses':syntheses}))

def check_exist(request, book_title):
    for b in Book.objects:
        pass

def check_ask(request):
    if request.method == 'POST':
        return HttpResponseRedirect('/')