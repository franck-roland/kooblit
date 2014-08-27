import pymill

from django.conf import settings
# model
from usr_management.models import Syntheses
from manage_books_synth.models import Book
# rendu
from django.shortcuts import render, render_to_response
from django.template import RequestContext

from django.http import HttpResponseRedirect, HttpResponse, Http404

# decorateur
from django.views.decorators.http import require_GET

# Create your views here.


def cart_details(request):
    if request.method == 'POST':
        if request.POST.get('synthese_id', ''):
            if request.POST['synthese_id'] in request.session.get('cart', ''):
                request.session['cart'].remove(request.POST['synthese_id'])
                request.session.modified = True
                request.nbre_achats -= 1
        else:
            raise Http404()
    cart = request.session.get('cart', [])
    cart = [("".join(("Kooblit de ", Book.objects.get(id=Syntheses.objects.get(id=i).livre_id).title, " par ",
                      Syntheses.objects.get(id=i).user.username)), Syntheses.objects.get(id=i).prix) for i in cart]
    cart_ids = request.session.get('cart', [])
    results = zip(cart, cart_ids)
    total = sum((i[1] for i in cart))
    return render_to_response('cart.html', RequestContext(request, {'results': results, 'total': total}))


def paiement(request):
    cart = request.session.get('cart', [])
    if cart:
        if request.method == 'POST':
            p = pymill.Pymill(settings.PAYMILL_PRIV)
            payment = p.new_card(token=request.POST['paymillToken'])
            payement_id = payment.id
            transaction = p.transact(
                amount=sum([int(float(Syntheses.objects.get(id=i).prix) * 100) for i in cart]),
                currency='EUR',
                description='Test Transaction',
                payment=payement_id
            )
            print transaction.status
            print payement_id
        total = sum((Syntheses.objects.get(id=i).prix for i in cart))
        return render_to_response('paiement.html', RequestContext(request, {'total': str(total).replace(",", ".")}))
    raise Http404()
