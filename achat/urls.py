from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('achat.views',
    url(r'^details$', 'cart_details', name='cart_details'),    
    url(r'^paiement$', 'paiement', name='paiement'),    
)
