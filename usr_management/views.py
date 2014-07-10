from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, Http404

# from django.contrib.auth.forms import UserCreationForm
from .forms import UserCreationFormKooblit
from django.contrib.auth.models import User
from .models import Verification, UserKooblit
from django.contrib.auth import authenticate, login
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

# Emails
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context

#JSON
import json

from django.template import RequestContext

import hashlib

def computeEmail(username, email, validation_id):
    htmly = get_template('email.html')
    d = Context({'username': username, 'validation_id': validation_id})
    subject, from_email, to = ('Welcome to Kooblit!!', 
                                'noreply@kooblit.com', email)
    html_content = htmly.render(d)
    msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
    msg.content_subtype = "html"
    msg.send()

def computeNewValidation(username):
    user = UserKooblit.objects.get(username=username)
    val = Verification(user=user, verification_id=hashlib.sha256(username).hexdigest())
    val.save()
    return val

def try_login(request, username, password, next_url):
    try:
        user = authenticate(username=username, password=password)
        if user is not None:
            user_kooblit = UserKooblit.objects.get(username=user.username)
            if user.is_active and user_kooblit.is_confirmed:
                login(request, user)
                return HttpResponseRedirect(next_url)
            elif not user.is_active:
                return HttpResponse("Your Kooblit account is disabled.")
            else:
                return render(request, 'baseMessages.html', {
                'message': 'Vous devez activer votre compte.',
                })
        else:
            return HttpResponse("Mauvais mot de passe ou identifiant")
    except MultiValueDictKeyError, e:
        raise
    except UserKooblit.DoesNotExist, e:
        return HttpResponse("Mauvais mot de passe ou identifiant")
    except Exception, e:
        raise

def contact(request):
    try:
        next_url = request.GET['next']
    except MultiValueDictKeyError, e:
        next_url = "/"
    except Exception:
        raise

    if not request.user.is_authenticated():
        if request.method == 'POST' : # If the form has been submitted...
            form = UserCreationFormKooblit(request.POST) # A form bound to the POST data

            # Check if it's a login
            try:
                username = request.POST['username_log']
                password = request.POST['password_log']
                return try_login(request, username, password, next_url)
            except MultiValueDictKeyError, e:
                pass
            except Exception, e:
                raise
                    
            # New user
            if form.is_valid(): # All validation rules pass
                username = form.cleaned_data.get("username")
                password = form.cleaned_data.get("password1")
                email = form.cleaned_data.get("email")
                form.save()
                val = computeNewValidation(username)
                computeEmail(username, email, val.verification_id)
                return HttpResponseRedirect(next_url)

        else:
            form = UserCreationFormKooblit() # An unbound form

        return render(request, 'contact.html', {
            'form': form,'next_url': next_url,
            })
    else:
        return HttpResponseRedirect(next_url)



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
            username = val.user.username
            password = val.user.password
            # import pdb;pdb.set_trace()
            val.delete()
            

            user = User.objects.get(username=username)
            if user is not None:
                if user.is_active:
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    login(request, user)
            # return HttpResponse("")
                    return render(request, 'baseMessages.html', {
                    'message': 'Votre compte Kooblit est active!',
                    })
            return HttpResponse("Your Kooblit account is disabled.")    
        else:
            return HttpResponse("Your Kooblit account is disabled.")
    except Verification.DoesNotExist, e:
        raise Http404()

@login_required
def user_suppression(request):
    user = request.user
    user.delete()
    return HttpResponseRedirect('/') # Redirect after POST

@login_required
def user_profil(request, username):
    user_kooblit = UserKooblit.objects.get(username=username)
    if user_kooblit.is_active and user_kooblit.is_confirmed:   
        return render(request, 'dashboard/index_profile.html', RequestContext(request, {'user_kooblit': user_kooblit}))
    else:
        raise Http404()

def check_exist(request):
    response_data = {}
    response_data['result'] = 'success'
    if request.method == 'GET':
        kwargs = {}
        username = request.GET.get('username','')
        if not username:
            mail = request.GET.get('email','')
            if not mail:
                return HttpResponse(json.dumps(response_data), content_type="application/json")    
            kwargs['email'] = mail
        else:
            kwargs['username'] = username
        try:
            user_kooblit = UserKooblit.objects.get(**kwargs)
            response_data['result'] = 'failed'
            response_data['message'] = "L'utilisateur existe deja"
        except UserKooblit.DoesNotExist, e:
            pass
        except Exception:
            raise    
    return HttpResponse(json.dumps(response_data), content_type="application/json")