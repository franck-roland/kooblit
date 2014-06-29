from django.shortcuts import render
from django.http import HttpResponseRedirect
# from django.contrib.auth.forms import UserCreationForm
from .forms import UserCreationForm
# Create your views here.

def contact(request):
    if request.method == 'POST': # If the form has been submitted...
        # ContactForm was defined in the previous section
        form = UserCreationForm(request.POST) # A form bound to the POST data
        import pdb; pdb.set_trace()
        if form.is_valid(): # All validation rules pass
            form.save()
            # Process the data in form.cleaned_data
            # ...
            return HttpResponseRedirect('/thanks/') # Redirect after POST
    else:
        form = UserCreationForm() # An unbound form

    return render(request, 'contact.html', {
        'form': form,
    })