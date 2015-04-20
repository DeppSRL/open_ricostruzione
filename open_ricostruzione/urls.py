from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin
from django.views.generic.base import TemplateView
from rest_framework import routers
from open_ricostruzione.views import StaticPageView, PageNotFoundTemplateView, HomeView, \
    LocalitaView, DonazioniListView, TipoImmobileView, SoggettoAttuatoreView, TipoSoggettoAttuatoreView, \
    ListaImpreseView, ImpresaDetailView, InterventoProgrammaView, InterventoRedirectView, ImpresaRedirectView, ListaInterventiView


from open_ricostruzione.viewsets import DonazioneViewSet, InterventoProgrammaViewSet


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'interventi_programma', InterventoProgrammaViewSet)
router.register(r'donazioni', DonazioneViewSet)

admin.autodiscover()
urlpatterns = patterns('',
                       # ADMIN urls
                       # Uncomment the admin/doc line below to enable admin documentation:
                       url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
                       # Uncomment the next line to enable the admin:
                       url(r'^admin/', include(admin.site.urls)),
                       # select2
                       url(r'^select2/', include('django_select2.urls')),
                       #  DJANGO FRONT URLS
                       url(r'^front-edit/', include('front.urls')),
                       url(r'^pages/chi-siamo', StaticPageView.as_view(), name='chi-siamo'),
                       url(r'^pages/faq', StaticPageView.as_view(), name='faq'),

                       # Django REST FRAMEWORK API urls
                       url(r'^api/', include(router.urls)),
                       url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

                       # robots.txt
                       url(r'^robots\.txt$', include('robots.urls')),
                       url(r'^page-not-found$', PageNotFoundTemplateView.as_view(), name='404'),

                       # Work in progress url
                       # url(r'^.*$', TemplateView.as_view(template_name='lavorincorso.html')),

                       url(r'^$', HomeView.as_view(), name='home'),
                       url(r'^intervento/search', InterventoRedirectView.as_view(), name='intervento-search'),
                       url(r'^impresa/search', ImpresaRedirectView.as_view(), name='impresa-search'),
                       url(r'^localita/(?P<slug>[-\w]+)/$', LocalitaView.as_view(), name='localita'),
                       url(r'^tipo_immobile/(?P<slug>[-\w]+)/$', TipoImmobileView.as_view(), name='tipo-immobile'),
                       url(r'^tipo_sogg_attuatore/(?P<slug>[-\w]+)/$', TipoSoggettoAttuatoreView.as_view(),
                           name='tipo-sogg-attuatore'),
                       url(r'^sogg_attuatore/(?P<slug>[-\w]+)/$', SoggettoAttuatoreView.as_view(),
                           name='sogg-attuatore'),
                       url(r'^intervento_programma/(?P<slug>[-\w]+)/$', InterventoProgrammaView.as_view(),
                           name='intervento-programma'),
                       url(r'^impresa/(?P<slug>[-\w]+)/$', ImpresaDetailView.as_view(), name='impresa'),
                       url(r'^lista_imprese/$', ListaImpreseView.as_view(), name='lista-imprese'),
                       url(r'^lista_interventi/$', ListaInterventiView.as_view(), name='lista-interventi'),
                       url(r'^lista_donazioni/$', DonazioniListView.as_view(), name='donazioni'),
                       # url(r'^list$', interventi_list)

)

if settings.INSTANCE_TYPE == 'development':
    urlpatterns += patterns('',
                            url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT,}),
                            # todo: remove following url
                            url(r'^venn_test/$', TemplateView.as_view(template_name='venn_test.html')),
    )