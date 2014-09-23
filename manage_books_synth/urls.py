from django.conf import settings
from django.conf.urls import patterns, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
                       # Examples:
                       url(r'^(?P<book_title>.{1,' + str(settings.MAX_BOOK_TITLE_LEN) + '})/post/(?P<author_username>.{1,30})$', 'manage_books_synth.views.upload_file', name='post'),
                       url(r'^(?P<book_title>.{1,' + str(settings.MAX_BOOK_TITLE_LEN) + '})/post/', 'manage_books_synth.views.upload_medium', name='post_medium'),
                       url(r'^(?P<book_title>.{1,' + str(settings.MAX_BOOK_TITLE_LEN) + '})/search/$', 'manage_books_synth.views.book_search', name='search'),
                       url(r'^(?P<book_title>.{1,' + str(settings.MAX_BOOK_TITLE_LEN) + '})/ask/$', 'manage_books_synth.views.demande_livre', name='ask'),
                       url(r'^(?P<book_title>.{1,' + str(settings.MAX_BOOK_TITLE_LEN) + '})/details$', 'manage_books_synth.views.selection', name='selection'),
                       url(r'^(?P<book_title>.{1,' + str(settings.MAX_BOOK_TITLE_LEN) + '})/$', 'manage_books_synth.views.book_detail', name='details'),
                       )
