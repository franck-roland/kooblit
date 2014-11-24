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
from django.template import RequestContext
from django.templatetags.static import static



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

#Taches asynchrones
from tasks import create_pdf, computeEmail


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
    inpart = ''.join((book_title, username)).encode("utf-8")
    part = hashlib.sha1(inpart).hexdigest()
    return ''.join(('/tmp/', part))


def get_tmp_medium_file(book_title, username):
    filename = get_name(book_title, username)
    try:
        with codecs.open(filename, 'r', encoding='utf-8') as newfile:
            return newfile.read()
    except IOError:
        return ''



def create_file_medium(request, s, book_title, username, prix=2, has_been_published=False):
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
            synthese._file_html = File(destination)
            # TODO: si deja publiée, est-ce possible de revenir en arriere
            synthese.has_been_published = has_been_published
        except Syntheses.DoesNotExist:
            synthese = Syntheses(_file_html=File(destination),
                                 user=user, livre_id=book.id, book_title=book.title,
                                 prix=2, has_been_published=has_been_published)
        if prix:
            synthese.prix = prix
        synthese.save()
        synthese.publish()
        create_pdf.delay(username, synthese)
    if has_been_published:
        os.remove(filename)


def clean_create_book(request, book_title, search_query=""):
    if search_query:
        amazon_request = AmazonRequest(search_query, settings.AMAZON_KEY, book_title=book_title, exact_match=1, delete_duplicate=0)
        s = amazon_request.find_in_existing_json()
    else:
        amazon_request = AmazonRequest(book_title, settings.AMAZON_KEY, exact_match=1, delete_duplicate=0)
        s = amazon_request.compute_args()
    s = [d for d in s]
    assert(len(s) > 0)
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


def create_book_if_doesnt_exist(request, book_title, search_query=""):
    try:
        Book.objects.get(title=book_title)
    except Book.DoesNotExist:
        return clean_create_book(request, book_title, search_query=search_query)


def send_alert(book_title):
    b = Book.objects.get(title=book_title)
    demandes = Demande.objects.filter(book=b.id)
    for d in demandes:
        user = d.user
        computeEmail.delay(user.username, book_title, alert=1)
        d.delete()


@login_required
@author_required
def upload_medium(request, book_title):
    book_title = urllib.unquote(book_title)
    username = request.user.username
    user = UserKooblit.objects.get(username=username)
    if request.method == 'POST':
        if "_publish" in request.POST:
            if not request.POST['prix']:
                price = 0
            else:
                price = float(request.POST['prix'])
                if price < 2:
                    price = 2
            create_file_medium(request, request.POST['q'], book_title, username, price,  has_been_published=True)
            book = Book.objects.get(title=book_title)
            synthese = Syntheses.objects.get(user=user, livre_id=book.id)
            if synthese.is_free:
                publication_message = u"""Votre koob de l'ouvrage <i>%s</i> a bien été publié. 
                    Pour assurer la qualité du service, nous ne permettons à nos utilisateurs de vendre que des koobs de qualité. 
                    C'est pour cela que pour être payant, un koob doit avoir obtenu au moins %i notes et une moyenne de %i/5. 
                    Votre koob sera donc disponible gratuitement jusqu'à ce qu'il réponde aux critères d'excellence de notre plateforme. 
                    Sachez que vous pouvez améliorer votre koob en y apportant des modifications à tout moment à partir de votre espace."""%(book_title ,settings.MIN_NOTE, settings.MIN_MEAN)
            else:
                publication_message = u"""Votre koob de l'ouvrage <i>%s</i> a bien été publié."""% book_title
            messages.success(request, publication_message)
            send_alert(book_title)
            print request
            return HttpResponseRedirect('/', request)
        elif "_quit" in request.POST:
            create_file_medium(request, request.POST['q'], book_title, username)
            messages.success(request, u'Votre koob pour le livre <i>"%s"</i> a bien été enregistré.' % book_title)
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
                synthese = None

        return render_to_response('edition_synthese.html', RequestContext(request, {'username': username, 'book': book, 'u_b': u_b, 'content': s, 'synthese': synthese}))




def create_and_get_synth(request, book_title, search_title):
    if create_book_if_doesnt_exist(request, book_title, search_query=search_title):
        raise Exception("Erreur de création du livre")

    b = Book.objects.get(title=book_title)

    # Update des recherches de ce livre
    res = Recherche.objects.filter(book=b)
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

    syntheses = Syntheses.objects.filter(livre_id=b.id, has_been_published=True)
    return syntheses


@login_required
def demande_livre(request, book_title):
    book_title = urllib.unquote(book_title)
    b = Book.objects.get(title=book_title)
    user = UserKooblit.objects.get(username=request.user.username)
    try:
        Demande.objects.get(user=user, book=b.id)
    except Demande.DoesNotExist:
        demande = Demande(user=user, book=b.id)
        demande.save()
        computeEmail.delay(user.username, book_title)
    return HttpResponse()


def selection(request, book_title):
    book_title = urllib.unquote(book_title)
    search_title = request.GET.get('search','')
    syntheses = create_and_get_synth(request, book_title, search_title)
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

    nb_syntheses = len(syntheses)

    if book.themes:
        genre = book.themes[0].theme
    else:
        genre = ""
    if book.langue:
        langue = book.langue
    else:
        langue = ''

    # Verifier s'il est necessaire de rajouter la demande
    add_modal = True
    if request.user.is_authenticated():
        user = UserKooblit.objects.get(username=request.user.username)
        try:
            Demande.objects.get(user=user, book=book.id)
            add_modal = False
        except Demande.DoesNotExist:
            pass

    return render_to_response('selection.html',
                              RequestContext(request,
                                             {'title': book.title, 'author': book.author[0], 'genre': genre, 'langue': langue, 'editeur': u_b.editeur,
                                              'img_url': u_b.image, 'nb_syntheses': nb_syntheses, 'description': book.description, 'buy_url': u_b.buy_url,
                                              'add_modal': add_modal}
                                             )
                              )


def valid_synthese_for_add(id_synthese, username):
    synthese = Syntheses.objects.get(id=id_synthese)
    return synthese.user.username != username and not UserKooblit.objects.filter(username=username, syntheses_achetees__synthese=synthese)



@add_to_cart
def book_detail(request, book_title):
    book_title = urllib.unquote(book_title)
    search_title = request.GET.get('search','')
    syntheses = create_and_get_synth(request, book_title, search_title)

    if request.user.is_authenticated():
        usr = UserKooblit.objects.get(username=request.user.username)
    else:
        usr = None
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

    return render_to_response(
        'details.html',
        RequestContext(request, {
            'title': book.title,
            'author': book.author[0],
            'img_url': u_b.image,
            'nb_syntheses': nb_syntheses,
            'syntheses': syntheses,
            'description': book.description,
            'buy_url': u_b.buy_url}))


