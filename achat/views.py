import json
import sys
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

import logging

logger = logging.getLogger(__name__)
paymill_response_code = {
    '10001': "General undefined response.",
    '10002': "Still waiting on something.",
    '20000': "General success response.",
    '40000': "General problem with data.",
    '40001': "General problem with payment data.",
    '40100': "Problem with credit card data.",
    '40101': "Problem with cvv.",
    '40102': "Card expired or not yet valid.",
    '40103': "Limit exceeded.",
    '40104': "Card invalid.",
    '40105': "Expiry date not valid.",
    '40106': "Credit card brand required.",
    '40200': "Problem with bank account data.",
    '40201': "Bank account data combination mismatch.",
    '40202': "User authentication failed.",
    '40300': "Problem with 3d secure data.",
    '40301': "Currency / amount mismatch",
    '40400': "Problem with input data.",
    '40401': "Amount too low or zero.",
    '40402': "Usage field too long.",
    '40403': "Currency not allowed.",
    '50000': "General problem with backend.",
    '50001': "Country blacklisted.",
    '50002': "IP address blacklisted.",
    '50003': "Anonymous IP proxy used.",
    '50100': "Technical error with credit card.",
    '50101': "Error limit exceeded.",
    '50102': "Card declined by authorization system.",
    '50103': "Manipulation or stolen card.",
    '50104': "Card restricted.",
    '50105': "Invalid card configuration data.",
    '50200': "Technical error with bank account.",
    '50201': "Card blacklisted.",
    '50300': "Technical error with 3D secure.",
    '50400': "Decline because of risk issues.",
    '50401': "Checksum was wrong.",
    '50402': "Bank account number was invalid (formal check).",
    '50403': "Technical error with risk check.",
    '50404': "Unknown error with risk check.",
    '50405': "Unknown bank code.",
    '50406': "Open chargeback.",
    '50407': "Historical chargeback.",
    '50408': "Institution / public bank account (NCA).",
    '50409': "KUNO/Fraud.",
    '50410': "Personal Account Protection (PAP).",
    '50500': "General timeout.",
    '50501': "Timeout on side of the acquirer.",
    '50502': "Risk management transaction timeout.",
    '50600': "Duplicate transaction.",
}


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
def webhook(request):
    if request.method == 'POST':
        json_string = request.META['wsgi.input'].read()
        d = json.loads(json_string)
        fraud = d['event']['event_resource']['is_fraud']
        try:
            trans = Transaction.objects.get(remote_id=d['event']['event_resource']['payment']['id'])
            return HttpResponse()
        except Transaction.DoesNotExist:
            raise Http404()
    else:
        raise Http404()
