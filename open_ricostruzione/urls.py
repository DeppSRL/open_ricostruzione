from django.conf.urls import patterns, include, url
from open_ricostruzione.views import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', HomeView.as_view(), name='home'),
    # url(r'^open_ricostruzione/', include('open_ricostruzione.foo.urls')),
    url(r'^progetto/(?P<slug>[-\w]+)$', ProgettoView.as_view(), name="progetto_detail"),
    url(r'^comune/(?P<slug>[-\w]+)$', ComuneView.as_view(), name="comune_detail"),
    url(r'^donazioni/$', DonazioneView.as_view(), name="donazioni"),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
