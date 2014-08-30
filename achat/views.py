import pymill
from hashlib import sha256
import datetime

from django.conf import settings
# model
from usr_management.models import Syntheses, Transaction, UserKooblit, Entree
from manage_books_synth.models import Book
# rendu
from django.shortcuts import render, render_to_response
from django.template import RequestContext

from django.http import HttpResponseRedirect, HttpResponse, Http404

# decorateur
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required

from django.views.decorators.csrf import csrf_exempt
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


@login_required
def paiement(request):
    cart = request.session.get('cart', [])
    if cart:
        if request.method == 'POST':
            p = pymill.Pymill(settings.PAYMILL_PRIVATE_KEY)

            payment = p.new_card(token=request.POST['paymillToken'])

            payement_id = payment.id
            transaction = p.transact(
                amount=sum([int(float(Syntheses.objects.get(id=i).prix) * 100) for i in cart]),
                currency='EUR',
                description='Test Transaction',
                payment=payement_id
            )
            trans = Transaction(user_from=UserKooblit.objects.get(username=request.user.username), remote_id=transaction.id)
            trans.save()
            for i in cart:
                e = Entree(user_dest=Syntheses.objects.get(id=i).user, montant=float(Syntheses.objects.get(id=i).prix),
                           transaction=trans)
                e.save()
        total = sum((Syntheses.objects.get(id=i).prix for i in cart))
        return render_to_response('paiement.html', RequestContext(request, {'total': str(total).replace(",", ".")}))
    raise Http404()


def crediter(user, montant):
    montant /= 2
    user.cagnotte += montant
    user.save()


# TODO SEND EMAIL AVEC FACTURE
@csrf_exempt
def webhook(request, _id_hook):
    if request.method == 'POST':
        print request.POST
        try:
            transaction = Transaction.objects.get(url=_id_hook)
            entrees = Entree.objects.filter(transaction=transaction)
            for e in entrees:
                crediter(e.user_dest, e.montant)
                e.delete()
            transaction.delete()

        except Transaction.DoesNotExist:
            raise Http404()
    else:
        raise Http404()
