from django.conf.urls import patterns, url


urlpatterns = patterns('',
    url(r'^$', 'search_engine.search_views.search_view', name='search')
)
