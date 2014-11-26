# -*- coding: utf-8 -*-
from random import randrange
import hashlib
import os
import re
import subprocess

from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect, HttpResponse, Http404, HttpResponseServerError

# from django.contrib.auth.forms import UserCreationForm
from .forms import UserCreationFormKooblit, ReinitialisationForm, DoReinitialisationForm, AddressChangeForm
from django.contrib.auth.models import User
from .models import Verification, UserKooblit, Reinitialisation, Syntheses, Address, Version_Synthese, Note, DueNote
from manage_books_synth.models import Book, UniqueBook
from manage_books_synth.models import Book
from django.contrib.auth import authenticate, login
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

# Settings
from django.conf import settings

#URLS
from django.core.urlresolvers import reverse

# Emails
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context

# Messages
from django.contrib import messages

# JSON
import json

from django.template import RequestContext

# Gestion du panier
from achat.utils import add_to_cart

from countries.data import COUNTRIES_DIC, COUNTRIES

# Fichiers
from django.core.files import File

from django.core.servers.basehttp import FileWrapper

from django.templatetags.static import static

from manage_books_synth.tasks import create_pdf

from utils import note_required

email_adresse_regex = "[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?"
email_match = re.compile(email_adresse_regex)

def computeEmail(request, username, email, validation_id):
    htmly = get_template('email.html')
    d = Context({'username': username, 'validation_id': validation_id, 'base_url': 'http://'+request.get_host()})
    subject, from_email, to = ('Welcome to Kooblit!!',
                               'no-reply@mail.kooblit.com', email)
    html_content = htmly.render(d)
    msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
    msg.content_subtype = "html"
    msg.send()


def computeEmail_reinitialisation(request, username, email, validation_id):
    htmly = get_template('email_reinitialisation.html')
    d = Context({'username': username, 'validation_id': validation_id, 'base_url': 'http://'+request.get_host()})
    subject, from_email, to = ('[Kooblit] Réinitialisation de mot de passe',
                               'noreply@kooblit.com', email)
    html_content = htmly.render(d)
    msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
    msg.content_subtype = "html"
    msg.send()


def computeNewValidation(username):
    user = UserKooblit.objects.get(username__iexact=username)
    val = Verification(user=user, verification_id=hashlib.sha256(username).hexdigest())
    val.save()
    return val


def try_login(request, username, password, next_url, form):
    login_error = "Mauvais mot de passe ou identifiant"
    is_email = email_match.match(username) != None
    if is_email:
        try:
            user_kooblit = UserKooblit.objects.get(email=username)
        except UserKooblit.DoesNotExist:
            return render(request, 'inscription.html', {
                'form': form, 'next_url': next_url, 'login_error': login_error
                })
    else:
        username = username.lower()
        try:
            user_kooblit = UserKooblit.objects.get(username__iexact=username)
        except UserKooblit.DoesNotExist:
            return render(request, 'inscription.html', {
                'form': form, 'next_url': next_url, 'login_error': login_error
                })

    username = user_kooblit.username
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active and user_kooblit.is_confirmed:
            login(request, user)
            return HttpResponseRedirect(next_url)
        elif not user.is_active:
            messages.error(request, "Votre compte est désactivé.")
        else:
            messages.warning(request, "Vous devez activer votre compte. <a href='/accounts/renvoi'> Renvoi </a>")
        return HttpResponseRedirect('/', RequestContext(request))
    else:
        return render(request, 'inscription.html', {
            'form': form, 'next_url': next_url, 'login_error': login_error
            })

def contact(request):
    try:
        next_url = request.GET['next']
    except MultiValueDictKeyError:
        next_url = "/"

    if not request.user.is_authenticated():
        if request.method == 'POST':  # If the form has been submitted...
            form = UserCreationFormKooblit(request.POST)  # A form bound to the POST data

            # Check if it's a login
            try:
                username = request.POST['username_log']
                password = request.POST['password_log']
                if next_url == "/":
                    next_url = reverse('usr_management:dashboard')
                return try_login(request, username, password, next_url, form)
            except MultiValueDictKeyError:
                pass

            # New user
            if form.is_valid():  # All validation rules pass
                next_url = '/' # TODO: connection autorisée pour un certain temps
                username = form.cleaned_data.get("username")
                password = form.cleaned_data.get("password1")
                email = form.cleaned_data.get("email")
                form.save()
                val = computeNewValidation(username)
                computeEmail(request, username, email, val.verification_id)
                messages.success(request, "Félicitation. Un email de confirmation vous a été envoyé.\
                    Vous ne pourrez vous connecter qu'après y avoir jeté un coup d'oeil")
                return HttpResponseRedirect(next_url, RequestContext(request))

        else:
            form = UserCreationFormKooblit()  # An unbound form

        return render(request, 'inscription.html', {
            'form': form, 'next_url': next_url,
            })
    else:
        return HttpResponseRedirect(next_url)


# Lecture des syntheses
def can_read(id_synthese, username):
    try:
        synthese = Syntheses.objects.get(id=id_synthese)
    except Syntheses.DoesNotExist:
        return False
    buyer = UserKooblit.objects.get(username=username)
    return synthese.user.username == username or UserKooblit.objects.filter(username=username, syntheses_achetees__synthese=synthese)




@login_required
def download_pdf(request, synthese_id):
    username = request.user.username
    if can_read(synthese_id, username):
        synth = Syntheses.objects.get(id=synthese_id)
        if synth.file_pdf.name == '0' or not synth.file_pdf.name:
            create_pdf(synth.user.username, synth)
        
        f = FileWrapper(synth.file_pdf)
        response = HttpResponse(f, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=synth_'+str(synthese_id)+'.pdf'
        return response
    raise Http404()


@login_required
def ajouter_synthese_gratuite(request, synthese_id):
    try:
        synthese = Syntheses.objects.get(id=synthese_id)
    except Syntheses.DoesNotExist:
        messages.warning(request, "La synthèse à laquelle vous essayez d'accéder n'est pas disponible")
        return HttpResponseRedirect("/")
    if not synthese.has_been_published:
        messages.warning(request, "La synthèse à laquelle vous essayez d'accéder n'est pas disponible")
        return HttpResponseRedirect("/")
    if not synthese.is_free:
        messages.warning(request, "La synthèse à laquelle vous essayez d'accéder n'est pas gratuite")
        return HttpResponseRedirect("/")

    if synthese.is_free and synthese.can_be_added_by(request.user.username):
        version_synthese = Version_Synthese.objects.get(synthese=synthese, version=synthese.version)
        user = UserKooblit.objects.get(username=request.user.username)
        user.syntheses_achetees.add(version_synthese)
        user.save()
        note = DueNote(user=user, synthese=synthese)
        note.save()
        messages.success(request, 
            "Vous accédez à cette synthèse gratuitement, nous vous demandons en contrepartie de lui donner une note après l'avoir consultée. Merci!")
    return HttpResponseRedirect(reverse('usr_management:lire_synthese', args=(synthese_id,)))


@login_required
def lire_synthese(request, synthese_id):
    username = request.user.username
    if can_read(synthese_id, username):
        synth = Syntheses.objects.get(id=synthese_id)
        book = Book.objects.get(title=synth.book_title)
        u_b = UniqueBook.objects.filter(book=book)[0]
        return render_to_response('lecture.html', RequestContext(request, {'synth': synth, 'book': book, 'u_b': u_b}))
    else:
        raise Http404()


@login_required
def noter_synthese(request, synthese_id):
    user = UserKooblit.objects.get(username=request.user.username)
    if request.method == "GET":
        note = float(int(request.GET["note"]))
        try:
            synth = Syntheses.objects.get(id=synthese_id)
            if not user.can_note(synth):
                raise Http404()
            else:
                note_total = synth.note_moyenne * synth.nbre_notes
                nbre_notes  = synth.nbre_notes + 1
                note_total += note
                synth.note_moyenne = note_total / nbre_notes
                synth.nbre_notes = nbre_notes
                synth.save()
                db_note = Note(user=user, synthese=synth, valeur=note)
                db_note.save()
                try:
                    due_note = DueNote.objects.get(user=user, synthese=synth)
                    due_note.delete()
                except DueNote.DoesNotExist:
                    pass
                print synth.nbre_notes, synth.note_moyenne

        except Syntheses.DoesNotExist:
            raise Http404()
        return HttpResponse()
    raise Http404()


# Use the login_required() decorator to ensure only those logged in can access the view.
@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the homepage.
    return HttpResponseRedirect('/')


def email_confirm(request, verification_id):
    try:
        val = Verification.objects.get(verification_id=verification_id)
        if val.user.is_active:
            val.user.is_confirmed = True
            val.user.save()
            # TODO: clean: unused password
            username = val.user.username
            password = val.user.password
            val.delete()

            user = User.objects.get(username__iexact=username)
            if user is not None:
                if user.is_active:
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    login(request, user)
                    messages.success(request, 'Votre compte Kooblit est activé!')
                    return HttpResponseRedirect('/', RequestContext(request))
            messages.error(request, "Votre compte kooblit est désactivé.")
            return HttpResponseRedirect('/', RequestContext(request))
        else:
            messages.error(request, "Votre compte kooblit est désactivé.")
            return HttpResponseRedirect('/', RequestContext(request))
    except Verification.DoesNotExist:
        raise Http404()


@login_required
def user_suppression(request):
    user = request.user
    user.delete()
    return HttpResponseRedirect('/')  # Redirect after POST


def get_syntheses_properties(syntheses):
    return [{
                "id": synth.id,
                "book_title": Book.objects.get(id=synth.livre_id).title,
                "author": synth.user.username,
                "prix": synth.prix,
                "nb_achat": synth.nb_achat,
                "note_moy": synth.note_moyenne,
                "gain": synth.nb_achat * synth.prix / 2,
            } for synth in syntheses]

@add_to_cart
def syntheses_from_user(request, user):
    syntheses = Syntheses.objects.filter(user=user, has_been_published=True).order_by('-date', '-note_moyenne')
    return render_to_response(
        'synth_list_user.html',
        RequestContext(request, {'syntheses': syntheses}))


@login_required
def user_dashboard(request):
    user_kooblit = UserKooblit.objects.get(username__iexact=request.user.username)
    username = user_kooblit.username
    if request.method == "POST":
        try:
            address = Address.objects.get(user=user_kooblit)
            form = AddressChangeForm(instance=address, data=request.POST)
            if form.is_valid():
                address = form.save()
                address.save()

        except Address.DoesNotExist:
            form = AddressChangeForm(data=request.POST)
            if form.is_valid():
                address = form.save(commit=False)
                address.user = user_kooblit
                address.save()
            
        response_errors = form.errors
        if 'first_name' in request.POST and request.POST['first_name'] != user_kooblit.first_name:
            user_kooblit.first_name = request.POST['first_name']
            user_kooblit.save()
        
        if 'last_name' in request.POST and request.POST['last_name'] != user_kooblit.last_name:
            user_kooblit.last_name = request.POST['last_name']
            user_kooblit.save()

        if 'username' in request.POST:
            username_post = request.POST['username']
            if username_post != username:
                try:
                    user2 = UserKooblit.objects.get(username__iexact=username_post)
                    if user2 == user_kooblit:
                        user_kooblit.username = username_post
                        user_kooblit.save()
                    else:
                        response_errors['username'] = 'Cet utilisateur existe déjà'
                except UserKooblit.DoesNotExist:
                    user_kooblit.username = username_post
                    user_kooblit.save()
        return HttpResponse(json.dumps(response_errors), content_type="application/json")
    else:
        loc_required = request.GET.get('loc','')
        next_url = request.GET.get('next','')
        form = AddressChangeForm()
        syntheses_achetees = [version_synth.synthese for version_synth in user_kooblit.syntheses_achetees.all()]
        syntheses_ecrites = Syntheses.objects.select_related('style','user').filter(user=user_kooblit, has_been_published=True)
        syntheses_en_cours = Syntheses.objects.select_related('style','user').filter(user=user_kooblit, has_been_published=False)
        total = user_kooblit.cagnotte
        try:
            adresse = Address.objects.get(user=user_kooblit)
        except Address.DoesNotExist:
            adresse = {'current_country':''}

        return render_to_response('profil.html', RequestContext(request, {'user_kooblit': user_kooblit, 'adresse': adresse, 'syntheses_achetees': syntheses_achetees, 
            'syntheses_ecrites': syntheses_ecrites, 'syntheses_en_cours': syntheses_en_cours, 
            'total': total, 'form': form, 'loc_required': loc_required, 'next_url': next_url,
             'COUNTRIES': [(i,j.encode('utf-8')) for i,j in COUNTRIES_DIC.items()]}))

@login_required
def user_profil(request, username):
    try:
        user_kooblit = UserKooblit.objects.get(username__iexact=username)
        if user_kooblit.is_active and user_kooblit.is_confirmed:
            return syntheses_from_user(request, user_kooblit)
        else:
            raise Http404()
    except UserKooblit.DoesNotExist:
        raise Http404()


def check_exist(request):
    response_data = {}
    response_data['result'] = 'success'
    if request.method == 'GET':
        kwargs = {}
        username = request.GET.get('username', '')
        if not username:
            mail = request.GET.get('email', '')
            if not mail:
                return HttpResponse(json.dumps(response_data), content_type="application/json")
            kwargs['email'] = mail
        else:
            kwargs['username__iexact'] = username
        try:
            # TODO: clean: unused user_kooblit
            user_kooblit = UserKooblit.objects.get(**kwargs)
            response_data['result'] = 'failed'
            response_data['message'] = "L'utilisateur existe deja"
        except UserKooblit.DoesNotExist:
            pass
    return HttpResponse(json.dumps(response_data), content_type="application/json")

def resend_verification(request):
    if request.method == 'POST':
        form = ReinitialisationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            try:
                user = UserKooblit.objects.get(email=email)
            # TODO: Message d'erreur email does not exist
            except UserKooblit.DoesNotExist:
                return HttpResponseRedirect('/', RequestContext(request))
            # Recherche de la verification
            val = Verification.objects.get(user=user)
            username = user.username
            computeEmail(request, username, email, val.verification_id)
            messages.success(request, "Félicitation. Un email de confirmation vous a été envoyé.\
                    Vous ne pourrez vous connecter qu'après y avoir jeté un coup d'oeil")
            return HttpResponseRedirect('/', RequestContext(request))
        else:
            return render(request, 'ask_reinitialisation.html', {'form': form})

    else:
        form = ReinitialisationForm()
        return render(request, 'ask_reinitialisation.html', {'form': form})

def ask_reinitialisation(request):
    if request.method == 'POST':
        form = ReinitialisationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            user = UserKooblit.objects.get(email=email)
            # Suppression d'une demande si déjà existante
            reinits = Reinitialisation.objects.filter(user=user)
            for reinit in reinits:
                reinit.delete()
            try:
                while True:
                    x = randrange(2 ** 64)
                    rnd = hashlib.sha1(''.join((email, str(x)))).hexdigest()
                    Reinitialisation.objects.get(rnd=rnd)
            except Reinitialisation.DoesNotExist:
                pass
            user = UserKooblit.objects.get(email=email)
            r = Reinitialisation(user=user, rnd=rnd)
            r.save()
            computeEmail_reinitialisation(request, user.username, email, rnd)
            messages.success(request, "Un email vous a été renvoyé")
            return HttpResponseRedirect('/', RequestContext(request))
        else:
            return render(request, 'ask_reinitialisation.html', {'form': form})

    else:
        form = ReinitialisationForm()
        return render(request, 'ask_reinitialisation.html', {'form': form})


def do_reinitialisation(request, r_id):
    try:
        reinit = Reinitialisation.objects.get(rnd=r_id)
    except Reinitialisation.DoesNotExist:
        raise Http404()
    if request.method == 'GET':
        form = DoReinitialisationForm()
        return render(request, 'do_reinitialisation.html', {'form': form})
    elif request.method == 'POST':
        form = DoReinitialisationForm(request.POST)
        if form.is_valid():
            user = reinit.user
            user.set_password(form.cleaned_data.get("mdp1"))
            user.save()
            reinit.delete()
            messages.success(request, 'Votre mot de passe a bien été changé')
            return HttpResponseRedirect('/', RequestContext(request))
        return render(request, 'do_reinitialisation.html', {'form': form})

