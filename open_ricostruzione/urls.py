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
    url(r'^progetti.json$', ProgettiJSONListView.as_view(), name="progetti_listJSON"),
    url(r'^comune/(?P<slug>[-\w]+)$', TerritorioView.as_view(), name="territorio_detail"),
    url(r'^progetti/(?P<tipologia>[-\w]+)/(?P<comune>[-\w]+)$', ProgettiTipologiaComune.as_view(), name="progetti-tipologia-comune"),
    url(r'^progetti-tipologia/(?P<tipologia>[-\w]+)$', ProgettiTipologia.as_view(), name="progetti-tipologia"),
    url(r'^progetti-comune/(?P<comune>[-\w]+)$', ProgettiComune.as_view(), name="progetti-comune"),
    url(r'^donazioni/$', DonazioneView.as_view(), name="donazioni-riepilogo"),
    url(r'^donazioni-tipologia/(?P<tipologia>[-\w]+)(\?page=(?P<page>[-\d]+))?$',  HomeView.as_view(), name="donazioni-tipologia"),
    url(r'^news/(?P<slug>[-\w]+)$', EntryView.as_view(), name="news"),
    url(r'^chi-siamo/$', HomeView.as_view(), name='home'),
    url(r'^contatti/$', HomeView.as_view(), name='home'),
    url(r'^download/$', HomeView.as_view(), name='home'),
    url(r'^licenza/$', HomeView.as_view(), name='home'),
    url(r'^faq/$', HomeView.as_view(), name='home'),
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
