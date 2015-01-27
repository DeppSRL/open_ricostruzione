from django.conf.urls import patterns, include, url
from open_ricostruzione.views import *
from django.views.generic.base import RedirectView
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',

    # todo: work in progress url to fix
    # url(r'^.*$', direct_to_template, {'template': 'lavorincorso.html'}),
    
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^progetto/(?P<slug>[-\w]+)$', ProgettoView.as_view(), name="progetto_detail"),
    url(r'^progetti.json$', ProgettiJSONListView.as_view(), name="progetti_listJSON"),
    url(r'^territori.json$', TerritoriJSONListView.as_view(), name="territori_listJSON"),
    url(r'^comune/(?P<slug>[-\w]+)$', TerritorioView.as_view(), name="territorio_detail"),
    url(r'^progetti/(?P<tipologia>[-\w]+)/(?P<comune>[-\w]+)$', ProgettiTipologiaComune.as_view(), name="progetti-tipologia-comune"),
    url(r'^progetti-tipologia/(?P<tipologia>[-\w]+)$', ProgettiTipologia.as_view(), name="progetti-tipologia"),
    url(r'^progetti-comune/(?P<comune>[-\w]+)$', ProgettiComune.as_view(), name="progetti-comune"),
    url(r'^donazioni-riepilogo/$', DonazioneView.as_view(), name="donazioni-riepilogo"),
    url(r'^donazioni/privati-cittadini',  RedirectView.as_view(url='/'), name="donazioni-tipologia-comune-privati"),
    url(r'^donazioni/altro',  RedirectView.as_view(url='/'), name="donazioni-tipologia-comune-altro"),
    url(r'^donazioni/(?P<tipologia>[-\w]+)/(?P<comune>[-\w]+)$', DonazioniTipologiaComune.as_view(), name="donazioni-tipologia-comune"),
    url(r'^donazioni-tipologia/privati-cittadini$',  RedirectView.as_view(url='/'), name="donazioni-tipologia-privati"),
    url(r'^donazioni-tipologia/altro$',  RedirectView.as_view(url='/'), name="donazioni-tipologia-altro"),
    url(r'^donazioni-tipologia/(?P<tipologia>[-\w]+)$',  DonazioniTipologia.as_view(), name="donazioni-tipologia"),
    url(r'^donazioni-comune/(?P<comune>[-\w]+)$',  DonazioniComune.as_view(), name="donazioni-comune"),
    url(r'^donazioni-completa/$',  DonazioniCompleta.as_view(), name="donazioni-completa"),
    url(r'^chi-siamo/$', TemplateView.as_view(template_name='chi-siamo.html'), name='chi-siamo'),
    url(r'^il-progetto/$', TemplateView.as_view(template_name='il-progetto.html'), name='il-progetto'),
    url(r'^contatti/$', TemplateView.as_view(template_name='contatti.html'), name="contatti"),
    url(r'^download/$', HomeView.as_view(), name='home'),
    url(r'^licenza/$', HomeView.as_view(), name='home'),
    url(r'^faq/$', FaqView.as_view(), name='faq'),
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEVELOPMENT:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$','django.views.static.serve',{
            'document_root': settings.MEDIA_ROOT,
        }))

