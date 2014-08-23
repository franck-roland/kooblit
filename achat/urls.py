from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('achat.views',
    url(r'^add$', 'add_to_cart', name='add_to_cart'),
    url(r'^details$', 'cart_details', name='cart_details'),    
)
