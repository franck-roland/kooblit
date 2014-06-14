from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'kooblit.views.homepage', name='homepage'),
    url(r'^(?P<essai>\d{1})$', 'kooblit.views.homepage', name='homepage'),
    url(r'^search/', include('search_engine.urls', namespace='search_engine')),
    # url(r'^blog/', include('blog.urls')),
    #url(r'^admin/', include(admin.site.urls)),
    
)
# + static(settings.STATIC_URL, settings.STATIC_ROOT)
