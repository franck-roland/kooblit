# -*- coding: utf-8 -*-
import os
import re
import datetime
import urllib
import hashlib
import codecs

# Settings
from django.conf import settings

# Fichiers
from django.core.files import File

# Rendu
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse, Http404

from django.contrib.auth.decorators import login_required
from django.template import Context
from django.template import RequestContext
from django.templatetags.static import static

# Emails
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

# Messages
from django.contrib import messages

# search for creation
from search_engine.AmazonRequest import AmazonRequest
from .models import Book, UniqueBook, Recherche, Theme
# Usr_management models
from usr_management.models import UserKooblit, Syntheses, Demande

from .forms import UploadFileForm

# Imaginary function to handle an uploaded file.
from HTMLParser import HTMLParser


# fichier docx
from docx import opendocx, getdocumentHtml

# Gestion du panier
from achat.utils import add_to_cart

re_get_summary = re.compile('.*<div class="summary">(.+)</div>.*')
re_get_extrait = re.compile('(.*)')


def check_html(file_name):
    parser = HTMLParser()
    with open(file_name, 'rb') as _f:
        parser.feed(_f.read())

from pyPdf import PdfFileReader
from pyPdf.utils import PdfReadError


def check_pdf(file_name):
    try:
        PdfFileReader(file(file_name, "rb"))
        return 0
    except PdfReadError:
        return 1
    except Exception:
        raise


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


def get_name(book_title, username):
    book_title = slugify(book_title)
    inpart = ''.join((book_title, username))
    part = hashlib.sha1(inpart).hexdigest()
    return ''.join(('/tmp/', part))


def get_tmp_medium_file(book_title, username):
    filename = get_name(book_title, username)
    try:
        with codecs.open(filename, 'r', encoding='utf-8') as newfile:
            return newfile.read()
    except IOError:
        return ''


def create_tmp_medium_file(request, s, book_title, username):
    create_book_if_doesnt_exist(request, book_title)
    filename = get_name(book_title, username)
    with codecs.open(filename, 'w', encoding='utf-8') as newfile:
        newfile.write(s)


def create_file_medium(s, book_title, username):
    user = UserKooblit.objects.get(username=username)
    book = Book.objects.get(title=book_title)
    filename = get_name(book_title, username)
    if '<br>' in s:
        s = s.replace('<br>', '<br/>')
    if '<script' in s:
        s = s.replace('<script', '\\<script')
    # if '<style' in s:
    #     x = s.split('<style')
    #     tmp = []
    #     for i in x:
    #         if '/style>' in i:
    #             tmp.append(i.split('/style>')[1])
    #         else:
    #             tmp.append(i)
    #     s = ''.join(tmp)

    with codecs.open(filename, 'w', encoding='utf-8') as newfile:
        newfile.write(s)

    with open(filename, 'r') as destination:
        try:
            synthese = Syntheses.objects.get(user=user, livre_id=book.id)
            synthese._file = File(destination)
            synthese._file_html = File(destination)
            synthese.save()
        except Syntheses.DoesNotExist:
            synthese = Syntheses(_file=File(destination), _file_html=File(destination),
                                 user=user, livre_id=book.id, prix=2)
            synthese.save()
    os.remove(filename)


def create_tmp_file(request, f, book_title, username):
    create_book_if_doesnt_exist(request, book_title)
    file_name = get_name(book_title, username)
    with open(file_name, 'wb') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    document = opendocx(file_name)
    with open(file_name + '.html', 'w') as newfile:
        paratextlist = getdocumentHtml(document)
        # Make explicit utf-8 version
        newparatextlist = []
        for paratext in paratextlist:
            newparatextlist.append(paratext.encode("utf-8"))
        page_html = ''.join(('<html>', ''.join(newparatextlist), '</html>'))
        # Join Paragraphs and print them
        newfile.write(page_html)

    user = UserKooblit.objects.get(username=username)
    book = Book.objects.get(title=book_title)
    # TODO: clean: title is not defined
    synthese = Syntheses.objects.filter(user=user, title=title, livre_id=book.id)
    return synthese


def create_file(book_title, username):
    user = UserKooblit.objects.get(username=username)
    book = Book.objects.get(title=book_title)
    filename = get_name(book_title, username)
    with open(filename, 'rb') as destination:
        with open(filename + '.html', 'r') as newfile:
            try:
                synthese = Syntheses.objects.get(user=user, livre_id=book.id)
                synthese._file = File(destination)
                synthese._file_html = File(newfile)
                synthese.save()
            except Syntheses.DoesNotExist:
                # TODO: clean: title is not defined
                synthese = Syntheses(_file=File(destination), _file_html=File(newfile),
                                     title=title, user=user, livre_id=book.id, prix=2)
                synthese.save()

    os.remove(filename)
    os.remove(filename + '.html')


def delete_tmp_file(book_title, title, username):
    filename = get_name(book_title, title, username)
    if os.path.isfile(filename):
        os.remove(filename)
    if os.path.isfile(filename + '.html'):
        os.remove(filename + '.html')


def clean_create_book(request, book_title):
    amazon_request = AmazonRequest(book_title, settings.AMAZON_KEY, exact_match=1, delete_duplicate=0)
    s = amazon_request.compute_args()
    s = [d for d in s if d['book_format'] == u'Broché' or d['book_format'] == 'Hardcover']
    s = [d for d in s if d['language'] == u'Français' or d['language'] == 'Anglais' or d['language'] == 'English']
    if not s:
        return 1
    first = s[0]
    try:
        book = Book.objects.get(title=first['title'][:256])
    except Book.DoesNotExist:
        book = Book(small_title=first['title'][:32], title=first['title'][:256],
                    author=[first['author']], description=first['summary'])
        book.save()
    if not book.langue and first['language']:
        book.langue = first['language']
        book.save()

    if first['theme']:
        theme = Theme.objects.get(theme=first['theme'])
        if theme not in book.themes:
            book.themes.append(theme)
            book.save()
    try:
        r = Recherche.objects.get(book=book, nb_searches=1)
    except Recherche.DoesNotExist:
        r = Recherche(book=book, nb_searches=1)
    r.save()
    for book_dsc in s:
        if not book_dsc['medium_image']:
            book_dsc['medium_image'] = 'http://' + request.get_host() + static('img/empty_gallery.png')
        if not book_dsc['image']:
            book_dsc['image'] = 'http://' + request.get_host() + static('img/empty_gallery.png')
        try:
            u_b = UniqueBook.objects.get(book=book, isbn=book_dsc['isbn'], image=book_dsc['image'], buy_url=book_dsc['DetailPageURL'])
            if u_b.medium_image != book_dsc['medium_image']:
                u_b.medium_image = book_dsc['medium_image']
        except UniqueBook.DoesNotExist:
            if book_dsc['image']:
                u_b = UniqueBook(book=book, isbn=book_dsc['isbn'], image=book_dsc['image'], buy_url=book_dsc['DetailPageURL'])
            else:
                u_b = UniqueBook(book=book, isbn=book_dsc['isbn'], image='http://' + request.get_host() + static('img/empty_gallery.png'), buy_url=book_dsc['DetailPageURL'])
        u_b.save()
        if book_dsc['editeur']:
            u_b.editeur = book_dsc['editeur']
            u_b.save()
    return 0


def create_book_if_doesnt_exist(request, book_title):
    try:
        Book.objects.get(title=book_title)
    except Book.DoesNotExist:
        clean_create_book(request, book_title)


def send_alert(book_title):
    b = Book.objects.get(title=book_title)
    demandes = Demande.objects.filter(book=b.id)
    for d in demandes:
        user = d.user
        computeEmail(user.username, book_title, alert=1)
        d.delete()


@login_required
def upload_file(request, book_title, author_username):
    username = request.user.username
    book_title = urllib.unquote(book_title)
    if not author_username:
        title = ''.join(("Kooblit de '", book_title, "' par ", username))
    else:
        title = ''.join(("Kooblit de '", book_title, "' par ", author_username))
    ret = {'form': '', 'prev': '', 'error': '', 'replace': ''}
    if username == author_username or not author_username:
        if request.method == 'POST':
            form = UploadFileForm(request.POST, request.FILES)
            if request.POST.get('oui', ''):
                try:
                    create_file(book_title, username)
                except IOError:
                    raise
                delete_tmp_file(book_title, title, username)
                messages.success(request, u'Votre fichier <i>"%s"</i> a bien été enregistré.' % title)
                send_alert(book_title)
                return HttpResponseRedirect('/', RequestContext(request))

            elif request.POST.get('oui_replace', ''):
                return HttpResponseRedirect(username, RequestContext(request, ret))

            elif request.POST.get('non_replace', ''):
                delete_tmp_file(book_title, title, username)
                form = UploadFileForm()
                ret['form'] = form
                return render_to_response('upload.html', RequestContext(request, {'form': form, 'prev': ''}))

            else:
                ret['form'] = form
                if request.POST.get('non', ''):
                    return render_to_response('upload.html',
                                              RequestContext(request, ret))
                else:
                    ret['form'] = form
                    if form.is_valid():
                        if create_tmp_file(request, request.FILES['file'], book_title, title, username):
                            ret['replace'] = 'oui'
                            ret['title'] = urllib.quote(username)
                            return render_to_response('upload.html', RequestContext(request, ret))
                        return HttpResponseRedirect(urllib.quote(username), RequestContext(request, ret))
        elif author_username:
            # TODO: clean: why getting those
            book = Book.objects.get(title=book_title)
            user = UserKooblit.objects.get(username=username)
            file_html = get_name(book_title, title, username) + '.html'
            # TODO: clean: useless try catch
            try:
                with open(file_html, 'r') as f:
                    s = f.read()
                ret['prev'] = s
            except IOError:
                raise
                # form = UploadFileForm()
                # ret['form'] = form
            return render_to_response('upload.html', RequestContext(request, ret))

        else:
            form = UploadFileForm()
            ret['form'] = form
            return render_to_response('upload.html', RequestContext(request, {'form': form, 'prev': ''}))


@login_required
def upload_medium(request, book_title):
    book_title = urllib.unquote(book_title)
    username = request.user.username
    user = UserKooblit.objects.get(username=username)
    if request.method == 'POST':
        if request.POST.get('e', ''):
            create_file_medium(request.POST['q'], book_title, username)
            messages.success(request, u'Votre synthèse pour le livre <i>"%s"</i> a bien été enregistré.' % book_title)
            send_alert(book_title)
            return HttpResponseRedirect('/', RequestContext(request))
        else:
            create_tmp_medium_file(request, request.POST['q'], book_title, username)
            return HttpResponse()
    else:
        s = get_tmp_medium_file(book_title, username)
        if not s:
            try:
                book = Book.objects.get(title=book_title)
                synthese = Syntheses.objects.get(user=user, livre_id=book.id)
                s = synthese._file_html.read()
            except (Syntheses.DoesNotExist, Book.DoesNotExist):
                pass
        return render_to_response('upload_medium.html', RequestContext(request, {'book_title': book_title, 'content': s}))


def computeEmail(username, book_title, alert=0):
    if not alert:
        htmly = get_template('email_demande_infos.html')
    else:
        htmly = get_template('email_synthese_dispo.html')
    email = UserKooblit.objects.get(username=username).email
    d = Context({'username': username, 'book_title': book_title})
    subject, from_email, to = ('[Kooblit] Alerte pour ' + book_title,
                               'noreply@kooblit.com', email)
    html_content = htmly.render(d)
    msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
    msg.content_subtype = "html"
    msg.send()


def book_search(request, book_title):
    book_title_save = book_title
    book_title = urllib.unquote(book_title)
    doesnotexist = {'title': book_title, 'url_title': urllib.unquote(book_title)}
    # if request.method == 'GET'
    if not request.META.get('HTTP_REFERER', '').startswith(''.join(('http://', request.META['HTTP_HOST'], '/search/?title='))):
        raise Http404()
    create_book_if_doesnt_exist(request, book_title)
    try:

        b = Book.objects.get(title=book_title)
        res = Recherche.objects(book=b)
        if not res:
            res = Recherche(book=b, nb_searches=1)
            res.save()
        else:
            res = res[0]

        if datetime.datetime.now().date() != res.day.date():
            res = Recherche(book=b, nb_searches=1)
        else:
            res.nb_searches += 1
        res.save()

        synthese = Syntheses.objects.filter(livre_id=b.id)
        if not synthese:
            return render_to_response('doesnotexist.html', RequestContext(request, doesnotexist))
        return HttpResponseRedirect('../details')
    except Book.DoesNotExist:
        return render_to_response('doesnotexist.html', RequestContext(request, doesnotexist))
    except Syntheses.DoesNotExist:
        if request.user.is_authenticated() and Demande.objects.filter(user=UserKooblit.get(username=request.user.username)):
            # return HttpResponseRedirect(reverse('book_management:details', book_title_save))
            return HttpResponseRedirect('../details')
        else:
            return render_to_response('doesnotexist.html', RequestContext(request, doesnotexist))

    raise Http404()


@login_required
def demande_livre(request, book_title):
    book_title = urllib.unquote(book_title)
    try:
        b = Book.objects.get(title=book_title)
    except Book.DoesNotExist:
        if not clean_create_book(request, book_title):
            b = Book.objects.get(title=book_title)
        else:
            raise Exception("Erreur de creation du livre")
    user = UserKooblit.objects.get(username=request.user.username)
    computeEmail(user.username, book_title)
    try:
        Demande.objects.get(user=user, book=b.id)
    except Demande.DoesNotExist:
        demande = Demande(user=user, book=b.id)
        demande.save()
    return HttpResponseRedirect('../details')


def selection(request, book_title):
    book_title = urllib.unquote(book_title)
    try:
        book = Book.objects.get(title=book_title)
    except Book.DoesNotExist:
        raise Http404()

    resu = [(res.nb_searches, res.day.strftime('%d, %b %Y')) for res in Recherche.objects(book=book)]
    if not book:
        return HttpResponseRedirect('/')
    try:
        u_b = UniqueBook.objects(book=book)[0]
    except IndexError:
        clean_create_book(request, book_title)
        u_b = UniqueBook.objects(book=book)[0]

    if not u_b.buy_url:
        clean_create_book(request, book_title)
        u_b = UniqueBook.objects(book=book)[0]

    syntheses = Syntheses.objects.filter(livre_id=book.id)
    nb_syntheses = len(syntheses)

    if book.themes:
        genre = book.themes[0].theme
    else:
        genre = ""
    if book.langue:
        langue = book.langue
    else:
        langue = ''
    return render_to_response('selection.html',
                              RequestContext(request,
                                             {'title': book.title, 'author': book.author[0], 'genre': genre, 'langue': langue, 'editeur': u_b.editeur,
                                              'img_url': u_b.image, 'nb_syntheses': nb_syntheses, 'description': book.description, 'buy_url': u_b.buy_url
                                              }
                                             )
                              )


def valid_synthese_for_add(id_synthese, username):
    synthese = Syntheses.objects.get(id=id_synthese)
    buyer = UserKooblit.objects.get(username=username)
    return synthese.user.username != username and synthese not in buyer.syntheses.all()



@add_to_cart
def book_detail(request, book_title):
    book_title = urllib.unquote(book_title)
    try:
        book = Book.objects.get(title=book_title)
    except Book.DoesNotExist:
        raise Http404()

    try:
        u_b = UniqueBook.objects(book=book)[0]
    except IndexError:
        clean_create_book(request, book_title)
        u_b = UniqueBook.objects(book=book)[0]

    if not u_b.buy_url:
        clean_create_book(request, book_title)
        u_b = UniqueBook.objects(book=book)[0]

    syntheses = Syntheses.objects.filter(livre_id=book.id)
    nb_syntheses = len(syntheses)

    bought = []
    for synt in syntheses:
        if request.user.is_authenticated() and not valid_synthese_for_add(synt.id, request.user.username):
            bought.append(True)
        else:
            bought.append(False)
    content = zip(syntheses, bought)

    return render_to_response(
        'details.html',
        RequestContext(request, {
            'title': book.title,
            'author': book.author[0],
            'img_url': u_b.image,
            'nb_syntheses': nb_syntheses,
            'content': content,
            'description': book.description,
            'buy_url': u_b.buy_url}))



def check_exist(request, book_title):
    for b in Book.objects:
        pass


def check_ask(request):
    if request.method == 'POST':
        return HttpResponseRedirect('/')
