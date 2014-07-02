from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse, Http404
# from django.contrib.auth.forms import UserCreationForm
from .forms import UserCreationFormKooblit
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
import hashlib

def computeEmail(username, validation_id):
    htmly = get_template('email.html')
    d = Context({'username': username, 'validation_id': validation_id})
    subject, from_email, to = ('Welcome to Kooblit!!', 
                                'noreply@kooblit.com', 'franck.l.roland@gmail.com')
    html_content = htmly.render(d)
    msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
    msg.content_subtype = "html"
    msg.send()

def computeNewValidation(username):
    user = UserKooblit.objects.get(username=username)
    val = Verification(user=user, verification_id=hashlib.sha256(username).hexdigest())
    val.save()
    return val

def try_login(username, password):
    try:
        user = authenticate(username=username, password=password)
    # import pdb;pdb.set_trace()
        if user is not None:
            if user.is_active and user.is_confirmed:
                login(request, user)
                return HttpResponseRedirect('/')
            elif not user.is_active:
                return HttpResponse("Your Kooblit account is disabled.")
            else:
                return HttpResponse("You need to activate your account.")
                # Return a 'disabled account' error message
        else:
            return HttpResponse("Mauvais mot de passe ou identifiant")
    except MultiValueDictKeyError, e:
        raise
    except Exception, e:
        raise

def contact(request):
    if request.method == 'POST': # If the form has been submitted...
        form = UserCreationFormKooblit(request.POST) # A form bound to the POST data

        if request.POST:
            # Check if it's a login
            try:
                username = request.POST['username_log']
                password = request.POST['password_log']
                return try_login(username, password)
            except MultiValueDictKeyError, e:
                pass
            except Exception, e:
                raise
                
        # New user
        if form.is_valid(): # All validation rules pass
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password1")
            form.save()
            user = authenticate(username=username, password=password)
            if user is not None:
                    if user.is_active:
                        login(request, user)
                        val = computeNewValidation(username)
                        computeEmail(username, val.verification_id)
                        return HttpResponseRedirect('/')            
            # Process the data in form.cleaned_data
            # ...
            return HttpResponseRedirect('/') # Redirect after POST
    else:
        form = UserCreationFormKooblit() # An unbound form

    return render(request, 'contact.html', {
        'form': form,
    })



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
            val.delete()
            return HttpResponse("Your Kooblit account is activated.")
        else:
            return HttpResponse("Your Kooblit account is disabled.")
    except Verification.DoesNotExist, e:
        raise Http404()

