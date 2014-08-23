# model
from usr_management.models import Syntheses
from manage_books_synth.models import Book
# rendu
from django.shortcuts import render, render_to_response
from django.template import RequestContext

from django.http import HttpResponseRedirect, HttpResponse, Http404

# decorateur
from django.views.decorators.http import require_POST

# Create your views here.
@require_POST
def add_to_cart(request):
	if not request.POST.get('synthese',[]):
		raise Http404()
	if not request.session['cart']:
		request.session.set_expiry(10*60)
		request.session['cart'] = [request.POST['synthese'],]
		return HttpResponse()
	else:
		request.session['cart'].append(request.POST['synthese'])


def cart_details(request):
	cart = request.session.get('cart',[])
	print cart
	cart = ["".join(( "Kooblit de ",Book.objects.get(id=Syntheses.objects.get(id=i).livre_id).title, "par ",
		Syntheses.objects.get(id=i).user.username)) for i in cart]
	return render_to_response('cart.html', RequestContext(request,{'cart': cart}))
