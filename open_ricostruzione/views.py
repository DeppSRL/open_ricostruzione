from django.core.exceptions import ObjectDoesNotExist
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

    programmazione_filters = None
    pianificazione_filters = None

    def __init__(self, programmazione_filters, pianificazione_filters):
        self.programmazione_filters = programmazione_filters
        self.pianificazione_filters = pianificazione_filters

    def get_aggr_tipologia_cedente(self,):
        values = []
        not_null = False
        for k, v in Donazione.get_aggregates_sum(**self.programmazione_filters).iteritems():
            if v:
                v = float(v)
                not_null = True
            else:
                continue

            values.append({'value': v, 'slug': k, 'label': Donazione.TIPO_CEDENTE.__getitem__(k)})

        if not_null:
            return values
        else:
            return None

    def _create_aggregate_int_progr(self, model):
        ##
        # creates the list of dict to be passed to the context.
        # calls the appropriate model function to get sums of the various categories of objects
        ##

        values = []
        for k, v in InterventoProgramma.get_aggregates_sum(model=model, **self.programmazione_filters).iteritems():
            if v:
                v = float(v)
            else:
                continue

            values.append({'value': v, 'slug': k, 'label': model.TIPOLOGIA.__getitem__(k)})

        return values

    def get_aggr_tipo_immobile(self,):
        return self._create_aggregate_int_progr(model=TipoImmobile,)

    def get_aggr_sogg_att(self,):
        return self._create_aggregate_int_progr(model=SoggettoAttuatore,)

    def fetch_interventi_programma(self, order_by, number=settings.N_PROGETTI_FETCH,):
        return InterventoProgramma.objects.filter(**self.programmazione_filters).order_by(order_by)[0:number]

    def get_pianificazione_status(self):

        piano_dict = {
            'count': InterventoPiano.objects.filter(**self.pianificazione_filters).count(),
            'money_value': InterventoPiano.objects.
            filter(**self.pianificazione_filters).aggregate(Sum('imp_a_piano'))['imp_a_piano__sum']
        }
        return piano_dict

    def get_programmazione_status(self):
        programmazione_dict = {
            'count': InterventoProgramma.objects.filter(**self.programmazione_filters).count(),
            'money_value':
                InterventoProgramma.objects.filter(**self.programmazione_filters).aggregate(Sum('importo_generale'))[
                    'importo_generale__sum']
        }

        return programmazione_dict

    def get_aggregates(self):
        ##
        # calls the functions to get the aggregates and returns a dict
        # all the function called depend on the filters passed to AggregatePageMixin on initialization
        # so they return context-based data
        ##

        agg_dict = {}
        agg_dict['ricostruzione_status'] = {
            'piano': self.get_pianificazione_status(),
            'programma': self.get_programmazione_status()
        }
        agg_dict['ricostruzione_status']['piano_percentage'] = 100.0 * (
            agg_dict['ricostruzione_status']['piano']['count'] / float(
                agg_dict['ricostruzione_status']['programma']['count']))

        # tipo immobile pie data
        agg_dict['tipo_immobile_aggregates_sum'] = self.get_aggr_tipo_immobile()
        # tipo sogg.att pie data
        agg_dict['sogg_att_aggregates_sum'] = self.get_aggr_sogg_att()
        # tipo sogg.att pie data
        agg_dict['tipologia_cedente_aggregates_sum'] = self.get_aggr_tipologia_cedente()

        # example interventi fetch
        agg_dict['interventi_top_importo'] = self.fetch_interventi_programma(order_by='-importo_generale')
        agg_dict['interventi_bottom_importo'] = self.fetch_interventi_programma(order_by='importo_generale')
        return agg_dict


class LocalitaView(TemplateView, AggregatePageMixin):
    template_name = 'localita.html'
    territorio = None
    vari_territori = False

    def get(self, request, *args, **kwargs):
        # get data from the request
        if kwargs['slug'] == 'vari-territori':
            self.vari_territori = True
            self.template_name = 'vari_territori.html'
        else:
            try:
                self.territorio = Territorio.objects.get(slug=kwargs['slug'])
            except ObjectDoesNotExist:
                return HttpResponseRedirect(reverse('territorio-not-found'))
        return super(LocalitaView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(LocalitaView, self).get_context_data(**kwargs)
        context['territorio'] = self.territorio
        context['vari_territori'] = self.vari_territori

        apm = AggregatePageMixin(programmazione_filters={'territorio':self.territorio}, pianificazione_filters={'intervento_programma__territorio': self.territorio})
        context.update(apm.get_aggregates())

        if self.vari_territori is False:
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


class HomeView(TemplateView, AggregatePageMixin):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        apm = AggregatePageMixin(programmazione_filters={}, pianificazione_filters={})
        context.update(apm.get_aggregates())
        return context
