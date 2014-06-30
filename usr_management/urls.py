from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'usr_management.views.contact', name='contact'),
    url(r'^logout$', 'usr_management.views.user_logout', name='logout'),
)
