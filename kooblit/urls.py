from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'kooblit.views.homepage', name='homepage'),
    url(r'^search/(?P<title>[ \w]{0,50})', 'kooblit.search_engine.views.search_view', name='search'),
    # url(r'^blog/', include('blog.urls')),
    #url(r'^admin/', include(admin.site.urls)),
    
) + static(settings.STATIC_URL, settings.STATIC_ROOT)
