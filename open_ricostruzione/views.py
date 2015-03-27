from django.core.exceptions import ObjectDoesNotExist
from django.http.response import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse, NoReverseMatch
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, DetailView, ListView, RedirectView
from django.db.models.aggregates import Sum
from django.conf import settings
from rest_framework import generics
from open_ricostruzione.forms import InterventoProgrammaSearchFormHome
from open_ricostruzione.models import InterventoProgramma, Donazione, InterventoPiano, TipoImmobile, SoggettoAttuatore, Impresa, Intervento
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
    attuazione_filters = None
    tipologia = None

    TERRITORIO = 0
    VARI_TERRITORI = 1
    TIPO_IMMOBILE = 2
    SOGG_ATT = 3
    HOME = 4

    def __init__(self, tipologia, programmazione_filters, pianificazione_filters, attuazione_filters):
        ##
        # initialize class with type and filter for programmazione / pianificazione
        ##

        self.tipologia = tipologia
        self.programmazione_filters = programmazione_filters
        self.pianificazione_filters = pianificazione_filters
        self.attuazione_filters = attuazione_filters


    def get_aggr_tipologia_cedente(self, ):
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
        return InterventoProgramma.get_type_aggregates(model=model, **self.programmazione_filters)

    def get_aggr_tipo_immobile(self, ):
        return self._create_aggregate_int_progr(model=TipoImmobile, )

    def get_aggr_sogg_att(self, ):
        return self._create_aggregate_int_progr(model=SoggettoAttuatore, )

    def fetch_interventi_programma(self, order_by, number=settings.N_PROGETTI_FETCH, ):
        return InterventoProgramma.objects.filter(**self.programmazione_filters).order_by(order_by)[0:number]

    def get_programmazione_status(self):
        return InterventoProgramma.programmati.filter(**self.programmazione_filters).with_count()

    def get_pianificazione_status(self):

        return {
            'count': InterventoPiano.objects.filter(**self.pianificazione_filters).count(),
            'money_value': InterventoPiano.objects.
            filter(**self.pianificazione_filters).aggregate(Sum('imp_a_piano'))['imp_a_piano__sum']
        }

    def get_attuazione_status(self):

        return {
            'count': Intervento.objects.filter(**self.attuazione_filters).count(),
            'money_value': Intervento.objects.filter(**self.attuazione_filters).aggregate(Sum('imp_congr_spesa'))['imp_congr_spesa__sum']
        }

    def get_aggregates(self):
        ##
        # calls the functions to get the aggregates and returns a dict
        # all the function called depend on the filters passed to AggregatePageMixin on initialization
        # so they return context-based data
        ##

        agg_dict = {'status': {
            'piano': self.get_pianificazione_status(),
            'programma': self.get_programmazione_status(),
            'attuazione': self.get_attuazione_status(),
        }}

        agg_dict['status']['piano']['percentage'] = 0.0
        agg_dict['status']['attuazione']['percentage'] = 0.0

        if agg_dict['status']['programma']['count'] > 0:
            agg_dict['status']['piano']['percentage'] = 100.0 * (
                agg_dict['status']['piano']['count'] / float(
                    agg_dict['status']['programma']['count']))

            agg_dict['status']['attuazione']['percentage'] = 100.0 * (
                agg_dict['status']['attuazione']['count'] / float(
                    agg_dict['status']['programma']['count']))


        # tipo immobile pie data
        if self.tipologia != self.TIPO_IMMOBILE:
            agg_dict['tipo_immobile_aggregates_sum'] = self.get_aggr_tipo_immobile()
        # tipo sogg.att data
        if self.tipologia != self.SOGG_ATT:
            agg_dict['sogg_att'] = self.get_aggr_sogg_att()
            # tipo sogg.att pie data
        if self.tipologia == self.HOME:
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

        if self.vari_territori:
            apm = AggregatePageMixin(
                tipologia=AggregatePageMixin.VARI_TERRITORI,
                programmazione_filters={'vari_territori': True},
                pianificazione_filters={'intervento_programma__vari_territori': True}
            )
        else:
            apm = AggregatePageMixin(
                tipologia=AggregatePageMixin.TERRITORIO,
                programmazione_filters={'territorio': self.territorio},
                pianificazione_filters={'intervento_programma__territorio': self.territorio}
            )

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


class TipoImmobileView(TemplateView, AggregatePageMixin):
    template_name = 'tipo_immobile.html'
    tipo_immobile = None

    def get(self, request, *args, **kwargs):
        # get data from the request
        try:
            self.tipo_immobile = TipoImmobile.objects.get(slug=kwargs['slug'])
        except ObjectDoesNotExist:
            return HttpResponseRedirect(reverse('tipo-immobile-not-found'))
        return super(TipoImmobileView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TipoImmobileView, self).get_context_data(**kwargs)
        context['tipo_immobile'] = self.tipo_immobile
        apm = AggregatePageMixin(
            tipologia=AggregatePageMixin.TIPO_IMMOBILE,
            programmazione_filters={'tipo_immobile': self.tipo_immobile},
            pianificazione_filters={'intervento_programma__tipo_immobile': self.tipo_immobile},
            attuazione_filters={'intervento_piano__intervento_programma__tipo_immobile=': self.tipo_immobile}
        )
        context.update(apm.get_aggregates())
        return context


class SoggettoAttuatoreView(TemplateView, AggregatePageMixin):
    template_name = 'sogg_att.html'
    sogg_att = None

    def get(self, request, *args, **kwargs):
        # get data from the request
        try:
            self.sogg_att = SoggettoAttuatore.objects.get(slug=kwargs['slug'])
        except ObjectDoesNotExist:
            return HttpResponseRedirect(reverse('404'))
        return super(SoggettoAttuatoreView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SoggettoAttuatoreView, self).get_context_data(**kwargs)
        context['sogg_att'] = self.sogg_att
        apm = AggregatePageMixin(
            tipologia=AggregatePageMixin.SOGG_ATT,
            programmazione_filters={'soggetto_attuatore': self.sogg_att},
            pianificazione_filters={'intervento_programma__soggetto_attuatore': self.sogg_att},
            attuazione_filters={'intervento_piano__intervento_programma__soggetto_attuatore': self.sogg_att}
        )
        context.update(apm.get_aggregates())
        return context


class HomeView(TemplateView, AggregatePageMixin):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        apm = AggregatePageMixin(
            tipologia=AggregatePageMixin.HOME,
            programmazione_filters={},
            pianificazione_filters={},
            attuazione_filters={}
        )
        context.update(apm.get_aggregates())
        return context


class TipoSoggettoAttuatoreView(ListView):
    template_name = 'tipo_sogg_att_list.html'
    tipologia_sogg_att = None

    def get(self, request, *args, **kwargs):
        if 'slug' not in kwargs:
            return HttpResponseRedirect(reverse('404'))

        # matches the name of the tipologia with the tipologia value to select the right set of sogg.attuatore
        t_list = filter(lambda x: x[1] == kwargs['slug'].upper(), SoggettoAttuatore.TIPOLOGIA._triples)
        if len(t_list) == 0:
            # if the slug does not match any tipologia slug -> 404
            return HttpResponseRedirect(reverse('404'))

        self.tipologia_sogg_att = t_list[0][0]

        # if the tipologia selected belongs to following categories which have only one sogg.att
        # then redirects to the sogg.att page
        tipologie_to_redirect = [
            SoggettoAttuatore.TIPOLOGIA.COMMISSARIO_DELEGATO,
            SoggettoAttuatore.TIPOLOGIA.PROV_INTERREGIONALE,
            SoggettoAttuatore.TIPOLOGIA.REGIONE
        ]

        if self.tipologia_sogg_att in tipologie_to_redirect:
            slug = SoggettoAttuatore.objects.get(tipologia=self.tipologia_sogg_att).slug
            return HttpResponseRedirect(reverse('sogg-attuatore', kwargs={'slug': slug}))

        return super(TipoSoggettoAttuatoreView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        return SoggettoAttuatore.objects.filter(tipologia=self.tipologia_sogg_att)


    def get_context_data(self, **kwargs):
        context = super(TipoSoggettoAttuatoreView, self).get_context_data(**kwargs)
        context['tipologia_sogg_att'] = SoggettoAttuatore.TIPOLOGIA[self.tipologia_sogg_att]
        return context


class ListaImpreseView(ListView):
    template_name = 'imprese_list.html'

    def get_queryset(self):
        return Impresa.objects.all().order_by('ragione_sociale')


class InterventoProgrammaView(DetailView):
    model = InterventoProgramma
    template_name = 'intervento_programma.html'


class ImpresaView(TemplateView):
    template_name = 'home.html'


# redirects visits coming from the autocomplete search to the intervento programma detail page
class InterventoRedirectView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):

        # get InterventoProgramma data from the request
        try:
            intervento_prog = get_object_or_404(InterventoProgramma,
                                                slug=self.request.GET.get('intervento_programma', 0))
        except Http404:
            return reverse('404')

        kwargs.update({'slug': intervento_prog.slug})

        # redirects to bilancio-overview for the latest bilancio available

        try:
            url = reverse('intervento-programma', args=args, kwargs=kwargs)
        except NoReverseMatch:
            return reverse('404')

        return url
