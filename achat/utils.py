# -*- coding: utf-8 -*-

# Messages
from django.contrib import messages

from usr_management.models import Syntheses

def add_to_cart(function):

    def wrap(request,*args,**kwargs):
        """ Ajout de d'une synthese au panier"""
        if request.method == 'POST' and request.POST.get('synthese', []):
            try:
                synthese = Syntheses.objects.get(id=int(request.POST['synthese']))
            except Syntheses.DoesNotExist:
                return function(request, *args, **kwargs)

            synthese_id = synthese.id
            if not request.session.get('cart', ''):
                request.session.set_expiry(60 * 60)
                if request.user.is_authenticated() and not synthese.can_be_added_by(request.user):
                    messages.warning(request, "Vous avez déjà acheté ou publié cette synthèse")
                else:
                    request.session['cart'] = [synthese_id]
                    messages.success(request, "Cette synthèse a bien été ajoutée à votre panier")
                    request.nbre_achats += 1
            else:
                if request.user.is_authenticated() and not synthese.can_be_added_by(request.user):
                    messages.warning(request, "Vous avez déjà acheté ou publié cette synthèse")

                elif synthese_id not in request.session['cart']:
                    request.session['cart'].append(synthese_id)
                    request.session.modified = True
                    messages.success(request, "Cette synthèse a bien été ajoutée à votre panier")
                    request.nbre_achats += 1
                else:
                    messages.warning(request, "Cette synthèse est déjà dans votre panier")
        return function(request, *args, **kwargs)

    return wrap