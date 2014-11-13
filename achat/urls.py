from django.conf.urls import patterns, url


urlpatterns = patterns('achat.views',
                       url(r'^details$', 'cart_details', name='cart_details'),
                       url(r'^paiement$', 'paiement', name='paiement'),
                       url(r'^ipn$', 'ipn', name='ipn'),
                       )
