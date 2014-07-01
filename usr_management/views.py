from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
# from django.contrib.auth.forms import UserCreationForm
from .forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
# Create your views here.

def contact(request):
    if request.method == 'POST': # If the form has been submitted...
        # ContactForm was defined in the previous section
        form = UserCreationForm(request.POST) # A form bound to the POST data
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
            form.save()
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=password)
            if user is not None:
                    if user.is_active:
                        login(request, user)
                        return HttpResponseRedirect('/')            
            # Process the data in form.cleaned_data
            # ...
            return HttpResponseRedirect('/') # Redirect after POST
    else:
        form = UserCreationForm() # An unbound form

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

