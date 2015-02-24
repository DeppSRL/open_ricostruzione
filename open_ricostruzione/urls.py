from django.conf.urls import patterns, include, url
from open_ricostruzione.views import *
from django.views.generic.base import RedirectView
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets
from django.contrib import admin


# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff')


# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)


admin.autodiscover()
urlpatterns = patterns('',
                       # Uncomment the admin/doc line below to enable admin documentation:
                       url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
                       # Uncomment the next line to enable the admin:
                       url(r'^admin/', include(admin.site.urls)),

                       # Django REST FRAMEWORK API urls

                       url(r'^api/', include(router.urls)),
                       url(r'^api/donazioni/$', DonazioneApiView.as_view(), name='api-donazioni-list'),
                       url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

                       # Work in progress url
                       # url(r'^.*$', TemplateView.as_view(template_name='lavorincorso.html')),

                       url(r'^$', HomeView.as_view(), name='home'),
                       url(r'^progetto/(?P<slug>[-\w]+)$', ProgettoView.as_view(), name="progetto_detail"),
                       url(r'^progetti.json$', ProgettiJSONListView.as_view(), name="progetti_listJSON"),
                       url(r'^territori.json$', TerritoriJSONListView.as_view(), name="territori_listJSON"),
                       url(r'^comune/(?P<slug>[-\w]+)$', TerritorioView.as_view(), name="territorio_detail"),
                       url(r'^progetti/(?P<tipologia>[-\w]+)/(?P<comune>[-\w]+)$', ProgettiTipologiaComune.as_view(),
                           name="progetti-tipologia-comune"),
                       url(r'^progetti-tipologia/(?P<tipologia>[-\w]+)$', ProgettiTipologia.as_view(),
                           name="progetti-tipologia"),
                       url(r'^progetti-comune/(?P<comune>[-\w]+)$', ProgettiComune.as_view(), name="progetti-comune"),
                       url(r'^donazioni-riepilogo/$', DonazioneView.as_view(), name="donazioni-riepilogo"),
                       url(r'^donazioni/privati-cittadini', RedirectView.as_view(url='/'),
                           name="donazioni-tipologia-comune-privati"),
                       url(r'^donazioni/altro', RedirectView.as_view(url='/'), name="donazioni-tipologia-comune-altro"),
                       url(r'^donazioni/(?P<tipologia>[-\w]+)/(?P<comune>[-\w]+)$', DonazioniTipologiaComune.as_view(),
                           name="donazioni-tipologia-comune"),
                       url(r'^donazioni-tipologia/privati-cittadini$', RedirectView.as_view(url='/'),
                           name="donazioni-tipologia-privati"),
                       url(r'^donazioni-tipologia/altro$', RedirectView.as_view(url='/'),
                           name="donazioni-tipologia-altro"),
                       url(r'^donazioni-tipologia/(?P<tipologia>[-\w]+)$', DonazioniTipologia.as_view(),
                           name="donazioni-tipologia"),
                       url(r'^donazioni-comune/(?P<comune>[-\w]+)$', DonazioniComune.as_view(),
                           name="donazioni-comune"),
                       url(r'^donazioni-completa/$', DonazioniCompleta.as_view(), name="donazioni-completa"),
                       url(r'^chi-siamo/$', TemplateView.as_view(template_name='chi-siamo.html'), name='chi-siamo'),
                       url(r'^il-progetto/$', TemplateView.as_view(template_name='il-progetto.html'),
                           name='il-progetto'),
                       url(r'^contatti/$', TemplateView.as_view(template_name='contatti.html'), name="contatti"),
                       url(r'^download/$', HomeView.as_view(), name='home'),
                       url(r'^licenza/$', HomeView.as_view(), name='home'),
                       url(r'^faq/$', FaqView.as_view(), name='faq'),
)

if settings.DEVELOPMENT:
    urlpatterns += patterns('',
                            url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
                                'document_root': settings.MEDIA_ROOT,
                            }))

