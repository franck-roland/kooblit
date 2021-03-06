from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings


admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^grappelli/', include('grappelli.urls')),  # grappelli URLS
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^$', 'kooblit.views.homepage', name='homepage'),
                       url(r'^(?P<alt>\d{1})/$', 'kooblit.views.homepage', name='homepage'),
                       url(r'^search/', include('search_engine.urls', namespace='search_engine')),
                       url(r'^accounts/', include('usr_management.urls', namespace='usr_management')),
                       url(r'^users/(?P<username>.{,30})/$', 'usr_management.views.user_profil', name='users'),
                       url(r'^book/', include('manage_books_synth.urls', namespace='book_management')),
                       url(r'^cart/', include('achat.urls', namespace='achat')),
                       )
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )