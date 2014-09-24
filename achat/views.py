# -*- coding: utf-8 -*-
from decimal import Decimal
import json
import pymill

from django.conf import settings
# model
from usr_management.models import Syntheses, Transaction, UserKooblit, Entree
from manage_books_synth.models import Book
# rendu
from django.shortcuts import render_to_response
from django.template import RequestContext

from django.http import HttpResponseRedirect, HttpResponse, Http404

# decorateur
from django.contrib.auth.decorators import login_required

from django.views.decorators.csrf import csrf_exempt

# Messages
from django.contrib import messages

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
    if request.user.is_authenticated():
        cart = clean_cart(cart, request.user.username)
    cart = [("".join(("Kooblit de ", Book.objects.get(id=Syntheses.objects.get(id=i).livre_id).title, " par ",
                      Syntheses.objects.get(id=i).user.username)), Syntheses.objects.get(id=i).prix) for i in cart]
    cart_ids = request.session.get('cart', [])
    results = zip(cart, cart_ids)
    total = sum((i[1] for i in cart))
    return render_to_response('cart.html', RequestContext(request, {'results': results, 'total': total}))


def ajouter_et_payer(buyer, synthese):
    buyer.syntheses.add(synthese)
    buyer.save()
    author = synthese.user
    price = synthese.prix
    # TODO: clean: remove those magic number (put them in a CONSTANT)
    # and why use decimal?
    PRIX_TRANSACTION = Decimal('0.0295') * price + Decimal('0.28')
    PRIX_TVA = Decimal('0.055') * price
    gain = price - PRIX_TVA - PRIX_TRANSACTION
    assert(gain > 0)
    author.cagnotte += gain / Decimal('2')
    author.save()


def clean_cart(cart, username):
    """ Enlève les synthèses qui ont déjà été achetées par l'utilisateur ou qui ont été publiées par lui """
    buyer = UserKooblit.objects.get(username=username)
    # TODO: clean:
    # buyer_syntheses_ids = [synth.id for synth in buyer.syntheses] (more simplifiable I think)
    # return Syntheses.objects.filter(id__in=cart).exclude(user__username=username, id__in=buyer_syntheses_ids)
    cart_final = []
    for id_synthese in cart:
        synthese = Syntheses.objects.get(id=id_synthese)
        if synthese.user.username != username and synthese not in buyer.syntheses.all():
            cart_final.append(id_synthese)
    return cart_final


@login_required
def paiement(request):
    cart = request.session.get('cart', [])
    if cart:
        if cart != clean_cart(cart, request.user.username):
            messages.warning(request, "Certains livres ont été enlevés de votre panier car vous en êtes soit l'auteur, soit vous l'avez déjà acheté")
            request.session['cart'] = clean_cart(cart, request.user.username)
            cart = request.session.get('cart', [])
            cart = [("".join(("Kooblit de ", Book.objects.get(id=Syntheses.objects.get(id=i).livre_id).title, " par ",
                              Syntheses.objects.get(id=i).user.username)), Syntheses.objects.get(id=i).prix) for i in cart]
            cart_ids = request.session.get('cart', [])
            results = zip(cart, cart_ids)
            total = sum((i[1] for i in cart))
            return render_to_response('cart.html', RequestContext(request, {'results': results, 'total': total}))
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
            buyer = UserKooblit.objects.get(username=request.user.username)
            trans = Transaction(user_from=buyer, remote_id=transaction.id)
            trans.save()
            for i in cart:
                e = Entree(user_dest=Syntheses.objects.get(id=i).user, montant=float(Syntheses.objects.get(id=i).prix),
                           transaction=trans)
                e.save()
                print type(transaction.response_code)
                if transaction.status == 'closed' and transaction.response_code == 20000:
                    # Ajouter la synthese aux syntheses achetées
                    synthese = Syntheses.objects.get(id=i)
                    ajouter_et_payer(buyer, synthese)
            if transaction.status == 'closed':
                request.session['cart'] = []
                messages.success(request, u'Votre commande a bien été enregistrée. Une facture vous sera envoyée à votre adresse email.')

                return HttpResponseRedirect('/')
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
