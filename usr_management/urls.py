from django.conf.urls import patterns, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^dashboard/$', 'usr_management.views.user_dashboard', name='dashboard'),
                       url(r'^login/$', 'usr_management.views.contact', name='login'),
                       url(r'^logout$', 'usr_management.views.user_logout', name='logout'),
                       url(r'^delete$', 'usr_management.views.user_suppression', name='delete'),
                       url(r'^confirmation/(?P<verification_id>[0-9a-f]{64})$', 'usr_management.views.email_confirm', name='email_confirm'),
                       url(r'^InputValidator$', 'usr_management.views.check_exist', name='validator'),
                       url(r'^renvoi/$', 'usr_management.views.resend_verification', name='resend_verification'),
                       url(r'^reinitialisation/$', 'usr_management.views.ask_reinitialisation', name='ask_reinitialisation'),
                       url(r'^reinit/(?P<r_id>[0-9a-f]{40})$', 'usr_management.views.do_reinitialisation', name='do_reinitialisation'),
                       url(r'^lire/(?P<synthese_id>[0-9a-f]{,64})$', 'usr_management.views.lire_synthese', name='lire_synthese'),
                       )
