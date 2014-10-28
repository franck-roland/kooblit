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
from usr_management.utils import author_required

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


def create_file_medium(request, s, book_title, username, has_been_published=False):
    # TODO: Utiliser la méthode publish de Syntheses
    create_book_if_doesnt_exist(request, book_title)
    user = UserKooblit.objects.get(username=username)
    book = Book.objects.get(title=book_title)
    try:
        synthese = Syntheses.objects.get(user=user, livre_id=book.id)
        synthese.publish()
        filename = synthese.filename
    except Syntheses.DoesNotExist:
        filename = Syntheses.get_filename_0(book_title, username)

    if '<br>' in s:
        s = s.replace('<br>', '<br/>')
    if '<script' in s:
        s = s.replace('<script', '\\<script')

    with codecs.open(filename, 'w', encoding='utf-8') as newfile:
        newfile.write(s)
    with open(filename, 'r') as destination:
        try:
            synthese = Syntheses.objects.get(user=user, livre_id=book.id)
            synthese._file = File(destination)
            synthese._file_html = File(destination)
            # TODO: si deja publiée, est-ce possible de revenir en arriere
            synthese.has_been_published = has_been_published
        except Syntheses.DoesNotExist:
            synthese = Syntheses(_file=File(destination), _file_html=File(destination),
                                 user=user, livre_id=book.id, prix=2, has_been_published=has_been_published)
        synthese.save()
        synthese.publish()

    if has_been_published:
        os.remove(filename)


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
@author_required
def upload_medium(request, book_title):
    book_title = urllib.unquote(book_title)
    username = request.user.username
    user = UserKooblit.objects.get(username=username)
    if request.method == 'POST':
        if "_publish" in request.POST:
            create_file_medium(request, request.POST['q'], book_title, username, has_been_published=True)
            messages.success(request, u'Votre synthèse pour le livre <i>"%s"</i> a bien été publié.' % book_title)
            send_alert(book_title)
            return HttpResponseRedirect('/', request)
        elif "_quit" in request.POST:
            create_file_medium(request, request.POST['q'], book_title, username)
            messages.success(request, u'Votre synthèse pour le livre <i>"%s"</i> a bien été enregistré.' % book_title)
            return HttpResponseRedirect('/', request)
        else:
            create_file_medium(request, request.POST['q'], book_title, username)
            return HttpResponse()
    else:
        try:
            book = Book.objects.get(title=book_title)
            u_b = UniqueBook.objects.filter(book=book)[0]
            if not u_b:
                messages.warning(request, "".join((u"Erreur lors de la création de la synthèse pour le live ", book_title)).encode("utf-8"))
                return HttpResponseRedirect('/', request)
        except Book.DoesNotExist:
            messages.warning(request, "".join((u"Erreur lors de la création de la synthèse pour le live ", book_title)).encode("utf-8"))
            return HttpResponseRedirect('/', request)
        s = get_tmp_medium_file(book_title, username)
        if not s:
            try:
                synthese = Syntheses.objects.get(user=user, livre_id=book.id)
                s = synthese._file_html.read()
            except Syntheses.DoesNotExist:
                pass
        return render_to_response('edition_synthese.html', RequestContext(request, {'username': username, 'book': book, 'u_b': u_b, 'content': s}))


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

    syntheses = Syntheses.objects.filter(livre_id=book.id, has_been_published=True)
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
    return synthese.user.username != username and not UserKooblit.objects.filter(username=username, syntheses_achetees__synthese=synthese)



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

    syntheses = Syntheses.objects.filter(livre_id=book.id, has_been_published=True)
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
