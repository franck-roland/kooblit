from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
# from django.contrib.auth.forms import UserCreationForm
from .forms import UserCreationFormKooblit
from django.contrib.auth import authenticate, login
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
# Create your views here.
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context


def computeEmail(username):
    htmly = get_template('email.html')
    d = Context({ 'username': username })
    subject, from_email, to = ('Welcome to Kooblit!!', 
                                'noreply@kooblit.com', 'franck.l.roland@gmail.com')
    html_content = htmly.render(d)
    msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
    msg.content_subtype = "html"
    msg.send()

def contact(request):
    if request.method == 'POST': # If the form has been submitted...
        # ContactForm was defined in the previous section
        form = UserCreationFormKooblit(request.POST) # A form bound to the POST data
        if request.POST:
            try:
                username = request.POST['username_log']
                password = request.POST['password_log']
                user = authenticate(username=username, password=password)
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        return HttpResponseRedirect('/')
                    else:
                        return HttpResponse("Your Kooblit account is disabled.")
                        # Return a 'disabled account' error message
                else:
                    return HttpResponse("Mauvais mot de passe ou identifiant")
            except MultiValueDictKeyError, e:
                pass
            except Exception, e:
                raise
                
        # Return an 'invalid login' error message.
        if form.is_valid(): # All validation rules pass
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password1")
            computeEmail(username)
            form.save()
            user = authenticate(username=username, password=password)
            if user is not None:
                    if user.is_active:
                        login(request, user)
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

