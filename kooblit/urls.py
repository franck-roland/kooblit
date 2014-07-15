from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^grappelli/', include('grappelli.urls')), # grappelli URLS
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'kooblit.views.homepage', name='homepage'),
    url(r'^(?P<essai>\d{1})$', 'kooblit.views.homepage', name='homepage2'),
    url(r'^search/', include('search_engine.urls', namespace='search_engine')),
    url(r'^accounts/', include('usr_management.urls', namespace='usr_management')),
    url(r'^users/(?P<username>.{,30})/$', 'usr_management.views.user_profil', name='users'),
    url(r'^book/', include('manage_books_synth.urls', namespace='book_management')),
)
# + static(settings.STATIC_URL, settings.STATIC_ROOT)
