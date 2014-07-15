from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^post/(?P<book_title>.{,32})$', 'manage_books_synth.views.book_detail', name='post' ),
    url(r'^search/(?P<book_title>.{,32})$', 'manage_books_synth.views.book_search', name='search' ),
    url(r'^details/(?P<book_title>.{,32})$', 'manage_books_synth.views.book_detail', name='details' ),
)
# + static(settings.STATIC_URL, settings.STATIC_ROOT)
