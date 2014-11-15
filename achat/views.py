# -*- coding: utf-8 -*-
import json
import pymill
import re

from django.conf import settings

# model
from usr_management.models import Syntheses, UserKooblit, Version_Synthese
from .models import Entree, Transaction
#URLS
from django.core.urlresolvers import reverse

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
from .libpayplug import redirect_payplug, ipn_payplug



URL_MATCH = re.compile('(http://.*?/)')

TVA = 0.05
TAXE_TRANSACTION = 0.03

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

def add_to_cart(request):
    if request.method == 'POST':
        if not request.POST.get('synthese', []):
            return

        synthese_id = int(request.POST['synthese'])
        if not request.session.get('cart', ''):
            request.session.set_expiry(60 * 60)
            if request.user.is_authenticated() and not valid_synthese_for_add(synthese_id, request.user.username):
                messages.warning(request, "Vous avez déjà acheté ou publié cette synthèse")
            else:
                request.session['cart'] = [synthese_id]
                messages.success(request, "Cette synthèse a bien été ajoutée à votre panier")
                request.nbre_achats += 1
        else:
            if request.user.is_authenticated() and not valid_synthese_for_add(synthese_id, request.user.username):
                messages.warning(request, "Vous avez déjà acheté ou publié cette synthèse")

            elif synthese_id not in request.session['cart']:
                request.session['cart'].append(synthese_id)
                request.session.modified = True
                messages.success(request, "Cette synthèse a bien été ajoutée à votre panier")
                request.nbre_achats += 1
            else:
                messages.warning(request, "Cette synthèse est déjà dans votre panier")
    return

def cart_details(request):
    if request.method == 'POST':
        if request.POST.get('synthese_id', ''):
            synthese_id = int(request.POST['synthese_id'])
            if synthese_id in request.session.get('cart', ''):
                request.session['cart'].remove(synthese_id)
                request.session.modified = True
                request.nbre_achats -= 1
        else:
            raise Http404()

    cart = request.session.get('cart', [])
    if request.user.is_authenticated():
        cart = clean_cart(cart, request.user.username)

    syntheses = (Syntheses.objects.get(id=i) for i in cart)
    cart = [
        {
            "id": synth.id,
            "book_title": synth.book_title,
            "author": synth.user.username,
            "prix": synth.prix,
        } for synth in syntheses
    ]

    return render_to_response(
        'cart.html',
        RequestContext(request, {
            'results': cart,
            'total': sum(synth['prix'] for synth in cart)}))


 def ajouter_et_payer(buyer, synthese):
    author = synthese.user
    price = float(synthese.prix)
    prix_HT = (price * (1 - TVA)) / 2
    gain = prix_HT - (price * TAXE_TRANSACTION)
    assert(gain > 0)
    author.cagnotte += gain
    author.save()
    version_synthese = Version_Synthese.objects.get(synthese=synthese, version=synthese.version)
    synthese.gain += gain
    synthese.nb_achat +=1
    synthese.save()
    version_synthese.gain += gain
    version_synthese.nb_achat += 1
    version_synthese.save()
    # buyer.syntheses.add(synthese)
    buyer.syntheses_achetees.add(version_synthese)
    buyer.save()


def clean_cart(cart, username):
    """ Enlève les synthèses qui ont déjà été achetées par l'utilisateur ou qui ont été publiées par lui """
    buyer = UserKooblit.objects.get(username=username)
    # TODO: refaire si acces a une seule version:
    buyer_syntheses_ids = [version_synth.synthese.id for version_synth in buyer.syntheses_achetees.all()]
    return [synth.id for synth in Syntheses.objects.filter(id__in=cart).exclude(user__username=username).exclude(id__in=buyer_syntheses_ids)]

@login_required
def paiement(request):
    # Clean the cart
    cart = request.session.get('cart', [])

    if not cart:
        return HttpResponseRedirect('/')

    if cart != clean_cart(cart, request.user.username):
        messages.warning(request, "Certains livres ont été enlevés de votre panier car vous en êtes soit l'auteur, soit vous l'avez déjà acheté")
        request.session['cart'] = clean_cart(cart, request.user.username)
        cart = request.session.get('cart', [])
        syntheses = (Syntheses.objects.get(id=i) for i in cart)
        cart = [
            {
                "id": synth.id,
                "book_title": synth.book_title,
                "author": synth.user.username,
                "prix": synth.prix,
            } for synth in syntheses
        ]

        return render_to_response(
            'cart.html',
            RequestContext(request, {
                'results': cart,
                'total': sum(synth['prix'] for synth in cart)}))
    return payplug_paiement(request)    

def payplug_paiement(request):
    s = request.build_absolute_uri()
    m = URL_MATCH.search(s)
    if settings.DEBUG:
        base_local = "http://dev.kooblit.com/"
    else:
        base_local = m.group(1)
    cart = request.session.get('cart', [])
    syntheses = (Syntheses.objects.get(id=i) for i in cart)
    buyer = UserKooblit.objects.get(username=request.user.username)

    params = {
        "ipn_url": "".join((base_local, reverse('achat:ipn')[1:])),
        "return_url": base_local,
        "cancel_url": base_local,
        "amount": int(sum(synth.prix for synth in syntheses) * 100), # Prix en centimes
        "first_name": buyer.first_name,
        "last_name": buyer.last_name,
        "email": buyer.email,
    }

    if request.method == 'POST':
        trans = Transaction(user_from=buyer, remote_id=0)
        trans.save()
        params["order"] = str(trans.id);
        for i in cart:
            synthese = Syntheses.objects.get(id=i)
            e = Entree(user_dest=Syntheses.objects.get(id=i).user, montant=float(Syntheses.objects.get(id=i).prix),
                       transaction=trans, synthese_dest=synthese)
            e.save()
        return redirect_payplug(params)

    total = sum((Syntheses.objects.get(id=i).prix for i in cart))
    return render_to_response('paiement.html', RequestContext(request, {'total': str(total).replace(",", ".")}))

@csrf_exempt
def ipn(request):
    return ipn_payplug(request)
# ajouter_et_payer(buyer, synthese)


@login_required
def paymill_paiement(request):
    cart = request.session.get('cart', [])

    if not cart:
        return HttpResponseRedirect('/')

    if cart != clean_cart(cart, request.user.username):
        messages.warning(request, "Certains livres ont été enlevés de votre panier car vous en êtes soit l'auteur, soit vous l'avez déjà acheté")
        request.session['cart'] = clean_cart(cart, request.user.username)
        cart = request.session.get('cart', [])
        syntheses = (Syntheses.objects.get(id=i) for i in cart)
        cart = [
            {
                "id": synth.id,
                "book_title": synth.book_title,
                "author": synth.user.username,
                "prix": synth.prix,
            } for synth in syntheses
        ]

        return render_to_response(
            'cart.html',
            RequestContext(request, {
                'results': cart,
                'total': sum(synth['prix'] for synth in cart)}))

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
            if len(cart) > 1:
                next_url = reverse('usr_management:dashboard')
            else:
                next_url = reverse('usr_management:lire_synthese', args=[cart[0]])
            request.session['cart'] = []
            messages.success(request, u'Votre commande a bien été enregistrée. Une facture vous sera envoyée à votre adresse email.')
            return HttpResponseRedirect(next_url)
    total = sum((Syntheses.objects.get(id=i).prix for i in cart))
    return render_to_response('paiement.html', RequestContext(request, {'total': str(total).replace(",", ".")}))


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
