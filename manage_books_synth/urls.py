from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^(?P<book_title>.{1,'+str(settings.MAX_BOOK_TITLE_LEN)+'})/post/(?P<title>.{,'+str(settings.MAX_BOOK_TITLE_LEN)+'})$', 'manage_books_synth.views.upload_file', name='post' ),
    url(r'^(?P<book_title>.{1,'+str(settings.MAX_BOOK_TITLE_LEN)+'})/search/$', 'manage_books_synth.views.book_search', name='search' ),
    url(r'^(?P<book_title>.{1,'+str(settings.MAX_BOOK_TITLE_LEN)+'})/ask/$', 'manage_books_synth.views.demande_livre', name='ask' ),
    url(r'^(?P<book_title>.{1,'+str(settings.MAX_BOOK_TITLE_LEN)+'})/$', 'manage_books_synth.views.book_detail', name='details' ),
)
# + static(settings.STATIC_URL, settings.STATIC_ROOT)
