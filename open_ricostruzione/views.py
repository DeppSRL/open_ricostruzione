from django.http.response import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView, DetailView, ListView
from django.db.models.aggregates import Sum
from django.conf import settings
from rest_framework import generics
from open_ricostruzione.models import InterventoProgramma, Donazione, InterventoPiano, TipoImmobile, SoggettoAttuatore
from territori.models import Territorio
from .serializers import DonazioneSerializer


class DonazioneApiView(generics.ListAPIView):
    """
    Returns a list of all authors.
    """
    model = Donazione
    serializer_class = DonazioneSerializer

    def get_queryset(self):
        return Donazione.objects.all()


class PageNotFoundTemplateView(TemplateView):
    template_name = '404.html'


class StaticPageView(TemplateView, ):
    template_name = 'static_page.html'


class DonazioniListView(ListView):
    paginate_by = 100
    model = Donazione
    template_name = 'donazioni_list.html'


class AggregatePageMixin(object):
    ##
    # Aggregati Page Mixin
    # stores the common function of all the aggregate views
    ##
    # todo: aggiungere la parte sull'attuazione
    
    @staticmethod
    def get_aggr_tipologia_cedente(**kwargs):
        values = []
        for k, v in Donazione.get_aggregates_sum(**kwargs).iteritems():
            if v:
                v = float(v)
            else:
                v = 0.0

            values.append({'value': v, 'slug': k, 'label': Donazione.TIPO_CEDENTE.__getitem__(k)})

        return values

    @staticmethod
    def _create_aggregate_int_progr(model, **kwargs):
        ##
        # creates the list of dict to be passed to the context.
        # calls the appropriate model function to get sums of the various categories of objects
        ##

        values = []
        for k, v in InterventoProgramma.get_aggregates_sum(model=model,**kwargs).iteritems():
            if v:
                v = float(v)
            else:
                v = 0.0

            values.append({'value': v, 'slug': k, 'label': model.TIPOLOGIA.__getitem__(k)})

        return values

    @staticmethod
    def get_aggr_tipo_immobile(**kwargs):
        return AggregatePageMixin._create_aggregate_int_progr(model=TipoImmobile, **kwargs)

    @staticmethod
    def get_aggr_sogg_att(**kwargs):
        return AggregatePageMixin._create_aggregate_int_progr(model=SoggettoAttuatore, **kwargs)


    @staticmethod
    def fetch_interventi_programma(order_by, number):
        return InterventoProgramma.objects.all().order_by(order_by)[0:number]


    @staticmethod
    def get_pianificazione_status(**kwargs):
        piano_dict = {
            'count': InterventoPiano.objects.filter(**kwargs).count(),
            'money_value': InterventoPiano.objects.filter(**kwargs).aggregate(Sum('imp_a_piano'))['imp_a_piano__sum']
        }
        return piano_dict

    @staticmethod
    def get_programmazione_status(**kwargs):
        programmazione_dict = {
            'count': InterventoProgramma.objects.filter(**kwargs).count(),
            'money_value': InterventoProgramma.objects.filter(**kwargs).aggregate(Sum('importo_generale'))['importo_generale__sum']
        }

        return programmazione_dict


class HomeView(TemplateView, AggregatePageMixin):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)

        context['ricostruzione_status'] = {
            'piano': AggregatePageMixin.get_pianificazione_status(),
            'programma': AggregatePageMixin.get_programmazione_status()
        }

        context['ricostruzione_status']['piano_percentage'] = 100.0 * (
            context['ricostruzione_status']['piano']['count'] / float(context['ricostruzione_status']['programma']['count']))


        # tipo immobile pie data
        context['tipo_immobile_aggregates_sum'] = AggregatePageMixin.get_aggr_tipo_immobile()
        # tipo sogg.att pie data
        context['sogg_att_aggregates_sum'] = AggregatePageMixin.get_aggr_sogg_att()
        # tipo sogg.att pie data
        context['tipologia_cedente_aggregates_sum'] = AggregatePageMixin.get_aggr_tipologia_cedente()
        # example interventi fetch
        interventi_top_importo = AggregatePageMixin.fetch_interventi_programma('-importo_generale', 5)
        interventi_bottom_importo = AggregatePageMixin.fetch_interventi_programma('importo_generale', 5)

        context['interventi_top_importo'] = interventi_top_importo
        context['interventi_bottom_importo'] = interventi_bottom_importo
        return context


class LocalitaView(DetailView, AggregatePageMixin):
    template_name = 'localita.html'
    model = Territorio
    context_object_name = "territorio"
    territorio = None

    def get(self, request, *args, **kwargs):
        # get data from the request
        try:
            self.territorio = self.get_object()
        except Http404:
            return HttpResponseRedirect(reverse('territorio-not-found'))
        return super(LocalitaView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(LocalitaView, self).get_context_data(**kwargs)

        context['ricostruzione_status'] = {
            'piano': AggregatePageMixin.get_pianificazione_status(intervento_programma__territorio=self.territorio),
            'programma': AggregatePageMixin.get_programmazione_status(territorio=self.territorio)
        }
        context['ricostruzione_status']['piano_percentage'] = 100.0 * (
            context['ricostruzione_status']['piano']['count'] / float(context['ricostruzione_status']['programma']['count']))

        # tipo immobile pie data
        context['tipo_immobile_aggregates_sum'] = AggregatePageMixin.get_aggr_tipo_immobile(territorio=self.territorio)
        # tipo sogg.att pie data
        context['sogg_att_aggregates_sum'] = AggregatePageMixin.get_aggr_sogg_att(territorio=self.territorio)
        # tipo sogg.att pie data
        context['tipologia_cedente_aggregates_sum'] = AggregatePageMixin.get_aggr_tipologia_cedente(territorio=self.territorio)


        # calculate the map bounds for the territorio
        bounds_width = settings.LOCALITA_MAP_BOUNDS_WIDTH

        context['map_bounds'] = \
            {'min':
                 {'lat': self.territorio.gps_lat - bounds_width,
                  'lon': self.territorio.gps_lon - bounds_width,
                 },
             'max':
                 {'lat': self.territorio.gps_lat + bounds_width,
                  'lon': self.territorio.gps_lon + bounds_width,
                 },
        }


        return context


class ProgettoListView(ListView):
    model = InterventoProgramma
    template_name = "tipologieprogetto.html"

    def get_context_data(self, **kwargs):
        context = super(ProgettoListView, self).get_context_data(**kwargs)
        context['SITE_URL'] = settings.PROJECT_ROOT
        return context

    def get_queryset(self):
    #        context = super(ProgettoListView, self).get_context_data(**kwargs)

        if 'qterm' in self.request.GET:
            qterm = self.request.GET['qterm']
            return InterventoProgramma.objects.filter(id_padre__isnull=True, denominazione__icontains=qterm)[0:50]
        else:
            return InterventoProgramma.objects.all()[0:50]
