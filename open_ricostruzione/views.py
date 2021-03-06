from decimal import Decimal
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse, NoReverseMatch
from django.shortcuts import get_object_or_404, render_to_response
from django.views.generic import TemplateView, DetailView, ListView, RedirectView
from django.db.models.aggregates import Count, Sum
from django_filters.views import FilterView
from django.conf import settings
from open_ricostruzione.models import InterventoProgramma, Donazione, TipoImmobile, SoggettoAttuatore, Impresa, DonazioneInterventoProgramma, Variante, InterventoPiano, Intervento, Cofinanziamento, Liquidazione, EventoContrattuale, Progetto
from territori.models import Territorio
from open_ricostruzione.utils import convert2dict
from open_ricostruzione.filters import InterventoProgrammaFilter, DonazioneFilter


class PageNotFoundTemplateView(TemplateView):
    template_name = '404.html'


class StaticPageView(TemplateView, ):
    template_name = 'static_page.html'


class FilterListView(FilterView):
    template_name = None
    model = None
    paginate_by = 100
    request = None
    _filterset = None
    filters = {}
    accepted_parameters = []
    validation = True

    def get_filter_set(self):
        raise NotImplemented

    def check_request_params(self):
        raise NotImplemented

    def get(self, request, *args, **kwargs):
        self.request = request
        self._filterset = self.get_filter_set()

        # in this way the objects coming out of the filter will be paginated
        self.queryset = self._filterset.qs

        # check GET parameters
        self.check_request_params()
        # if validation fails => redirect
        if self.validation is False:
            return HttpResponseRedirect(reverse('404'))
        return super(FilterListView, self).get(request, *args, **kwargs)


    def get_parameter(self, get_parameter, possible_values, **kwargs):
        model = kwargs.get('model', None)
        # get the parameters from the filter
        # if the value is not None
        # and is one of the possible values -> returns the value
        # else returns false
        slug_value = self._filterset.form.data.get(get_parameter, None)
        if slug_value is None:
            return slug_value
        elif slug_value not in possible_values:
            self.validation = False
            return False

        if model:
            return model.objects.get(slug=slug_value)

        return slug_value

    def get_context_data(self, **kwargs):
        context = super(FilterListView, self).get_context_data(**kwargs)
        context['request'] = self.request
        context.update(self.filters)
        return context


class InterventoProgrammaMapMixin(object):
    # sets the bounds for simple map display (POI map)

    def get_map_data(self):
        bounds_width = settings.LOCALITA_MAP_BOUNDS_WIDTH

        gps_lat = self.territorio.gps_lat
        gps_lon = self.territorio.gps_lon

        if self.intervento_programma.gps_lat:
            gps_lat = self.intervento_programma.gps_lat
        if self.intervento_programma.gps_lon:
            gps_lon = self.intervento_programma.gps_lon

        data = {}
        data['map_bounds'] = {'sw':
                    {'lat': gps_lat - bounds_width,
                     'lon': gps_lon - bounds_width,
                    },
                'ne':
                    {'lat': gps_lat + bounds_width,
                     'lon': gps_lon + bounds_width,
                    },
        }

        data['map_center'] = {'lat': gps_lat, 'lon': gps_lon}

        return data


class LocalitaMapMixin(object):
    # sets the bounds for simple map display (POI map)

    @property
    def get_map_data(self):
        bounds_width = settings.LOCALITA_MAP_BOUNDS_WIDTH
        data = {'map_pois': []}

        class MyObj(object):
            gps_lat=gps_lon=None

            def __init__(self, ip):
                self.gps_lat = ip.gps_lat
                self.gps_lon = ip.gps_lon

        sw = MyObj(self.territorio)
        ne = MyObj(self.territorio)
        # calculates map center, map N-east and S-west bounds

        for ip in self.interventi_programma:
            tooltip_text = ip.denominazione.title()
            if len(tooltip_text) > 60:
                tooltip_text = tooltip_text[:60]+"..."

            if ip.gps_lat is not None:
                if ip.gps_lat < sw.gps_lat:
                    sw.gps_lat = ip.gps_lat
                if ip.gps_lat > ne.gps_lat:
                    ne.gps_lat = ip.gps_lat
            else:
                ip.gps_lat = self.territorio.gps_lat

            if ip.gps_lon is not None:
                if ip.gps_lon < sw.gps_lon:
                    sw.gps_lon = ip.gps_lon

                if ip.gps_lon > ne.gps_lon:
                    ne.gps_lon = ip.gps_lon
            else:
                ip.gps_lon = self.territorio.gps_lon

            data['map_pois'].append({'lat': ip.gps_lat, 'lon': ip.gps_lon, 'tooltip_text': tooltip_text, 'tooltip_url': reverse('intervento-programma', args=(ip.slug,))})

        data['map_bounds'] = {
            'sw':
                    {'lat': sw.gps_lat - bounds_width,
                     'lon': sw.gps_lon - bounds_width,
                    },
            'ne':
                    {'lat': ne.gps_lat + bounds_width,
                     'lon': ne.gps_lon + bounds_width,
                    },
                }

        data['map_center'] = {
            'lat': (data['map_bounds']['sw']['lat']+data['map_bounds']['ne']['lat'])/2,
            'lon': (data['map_bounds']['sw']['lon']+data['map_bounds']['ne']['lon'])/2
        }

        return data


class ThematicMapMixin(object):
    map_filters = None

    def __init__(self, map_filters):
        # initialize map filters
        self.map_filters = map_filters

    @staticmethod
    def _get_territorio_set():
        return list(
            Territorio.objects. \
                filter(tipologia="C", regione="Emilia Romagna"). \
                order_by('denominazione'))


    @staticmethod
    def _create_map_values(data_list):

        data_dict = convert2dict(data_list, 'slug')
        map_values = []
        for t in ThematicMapMixin._get_territorio_set():
            sum = 0
            url = ''

            if t.istat_id in settings.COMUNI_CRATERE:
                url = reverse('localita', kwargs={'slug': t.slug})

            if data_dict.get(t.slug, None):
                value = data_dict[t.slug][0]['value']
                count = data_dict[t.slug][0]['count']

                if data_dict[t.slug][0].get('sum', None):
                    sum = data_dict[t.slug][0]['sum']
            else:
                value = None
                count = 0

            map_values.append(
                {
                    'label': t.nome_con_provincia,
                    'url': url,
                    'value': value,
                    'count': count,
                    'sum': sum,
                    'istat_code': "8{}".format(t.istat_id),
                }
            )
        return map_values

    def get_danno_values(self, page_type):
        # creates data struct for danno map:
        # for each territorio gathers: n. interventi and sum of interventi
        cache_key = "{}_map_danno_values".format(page_type)
        danno_values = cache.get(cache_key, None)

        if danno_values is None:

            danno_values = list(
                Territorio.objects. \
                    filter(tipologia="C", regione="Emilia Romagna"). \
                    filter(**self.map_filters). \
                    annotate(Sum('interventoprogramma__importo_generale')). \
                    annotate(Count('interventoprogramma__importo_generale')). \
                    values('slug', 'interventoprogramma__importo_generale__sum',
                           'interventoprogramma__importo_generale__count')
            )

            for item in danno_values:
                item['value'] = item['interventoprogramma__importo_generale__sum']
                item['count'] = item['interventoprogramma__importo_generale__count']

            danno_values = ThematicMapMixin._create_map_values(danno_values)
            cache.set(cache_key, danno_values, 60 * 5)

        return danno_values

    def get_attuazione_values(self, page_type):
        # creates data struct for attuazione map:
        # for each territorio gathers: n. interventi and sum of interventi

        cache_key = "{}_map_attuazione_values".format(page_type)
        attuazione_values = cache.get(cache_key, None)

        if attuazione_values is None:
            attuazione_values = list(
                Territorio.objects.filter(tipologia="C", regione="Emilia Romagna"). \
                    filter(**self.map_filters). \
                    annotate(Sum('interventoprogramma__interventopiano__intervento__imp_consolidato')). \
                    annotate(Sum('interventoprogramma__importo_generale')). \
                    values('slug',
                           'interventoprogramma__interventopiano__intervento__imp_consolidato__sum',
                           'interventoprogramma__importo_generale__sum'))

            attuazione_n_interventi = Territorio.objects. \
                filter(
                tipologia="C",
                regione="Emilia Romagna",
                interventoprogramma__interventopiano__intervento__isnull=False,
                **self.map_filters). \
                annotate(c=Count('interventoprogramma')).values('slug', 'c')

            n_interventi_dict = convert2dict(attuazione_n_interventi, 'slug')

            for item in attuazione_values:
                item['value'] = 0
                item['count'] = 0
                valore_attuaz = item['interventoprogramma__interventopiano__intervento__imp_consolidato__sum']
                item['sum'] = valore_attuaz
                valore_progr = item['interventoprogramma__importo_generale__sum']

                # add count of interventi in attuazione
                if n_interventi_dict.get(item['slug'], None):
                    item['count'] = n_interventi_dict[item['slug']][0]['c']

                if valore_progr and valore_progr != 0 and valore_attuaz:
                    item['value'] = 100.0 * float(valore_attuaz / valore_progr)
            attuazione_values = ThematicMapMixin._create_map_values(attuazione_values)
            cache.set(cache_key, attuazione_values, 60 * 5)

        return attuazione_values


class DonazioniListView(FilterListView):
    template_name = 'donazioni_list.html'
    model = Donazione
    don_filter = None
    accepted_parameters = ['tipologia_cedente', 'territorio__slug', 'interventi_programma__tipo_immobile__slug',
                           'interventi_programma__slug', 'page']

    def get_filter_set(self):
        return DonazioneFilter(self.request.GET,
                               queryset=Donazione.objects.all().select_related('territorio', 'donazione_intervento'))

    def check_request_params(self):

        # check that GET parameters are ONLY the ones in the accepted_params variable. if NOT -> redirect 404
        if not (set(self._filterset.form.data.keys()) <= set(self.accepted_parameters)):
            self.validation = False

        territori_set = Territorio.get_territori_cratere().values_list('slug', flat=True)
        self.filters['territorio_filter'] = self.get_parameter('territorio__slug', territori_set, model=Territorio)

        tipo_immobile_set = TipoImmobile.objects.all().values_list('slug', flat=True)
        self.filters['tipo_immobile_filter'] = self.get_parameter('interventi_programma__tipo_immobile__slug',
                                                                  tipo_immobile_set,
                                                                  model=TipoImmobile)

        interventi_programma_set = InterventoProgramma.objects.all().values_list('slug', flat=True)
        self.filters['interventi_programma_filter'] = self.get_parameter('interventi_programma__slug',
                                                                         interventi_programma_set,
                                                                         model=InterventoProgramma)

        tipologia_cedente_set = Donazione.TIPO_CEDENTE
        tc_val = self.get_parameter('tipologia_cedente', tipologia_cedente_set)
        # translate numeric value to string for display
        if tc_val:
            self.filters['tipologia_cedente_filter'] = tipologia_cedente_set._display_map[tc_val]

    def get_queryset(self):
        queryset = super(DonazioniListView, self).get_queryset().order_by('-importo')
        return queryset.select_related('territorio', 'donazione_intervento')


class InterventiListView(FilterListView):
    template_name = 'interventi_list.html'
    model = InterventoProgramma
    paginate_by = 50
    request = None
    filters = {}
    accepted_parameters = ['territorio__slug', 'tipo_immobile__slug', 'soggetto_attuatore__slug',
                           'soggetto_attuatore__tipologia', 'a_piano', 'in_attuazione', 'stato_attuazione',
                           'interventopiano__intervento__imprese__slug', 'vari_territori', 'page']
    validation = True

    def get_filter_set(self):
        return InterventoProgrammaFilter(
            self.request.GET,
            queryset=InterventoProgramma.objects.all().select_related('territorio')
        )

    def check_request_params(self):

        # check that GET parameters are ONLY the ones in the accepted_params variable. if NOT -> redirect 404
        if not (set(self._filterset.form.data.keys()) <= set(self.accepted_parameters)):
            self.validation = False

        territori_set = Territorio.get_territori_cratere().values_list('slug', flat=True)
        self.filters['territorio_filter'] = self.get_parameter('territorio__slug', territori_set, model=Territorio)

        vari_territori_set = ['False', 'True']
        self.filters['vari_territori_filter'] = self.get_parameter('vari_territori', vari_territori_set, )

        tipo_immobile_set = TipoImmobile.objects.all().values_list('slug', flat=True)
        self.filters['tipo_immobile_filter'] = self.get_parameter('tipo_immobile__slug', tipo_immobile_set,
                                                                  model=TipoImmobile)

        # if filter vari territori is True, there cannot be territorio filter on specific territorio
        if self.filters['vari_territori_filter'] == u'True' and self.filters['territorio_filter'] is not None:
            self.validation = False

        sogg_attuatore_set = SoggettoAttuatore.objects.all().values_list('slug', flat=True)
        self.filters['sogg_attuatore_filter'] = self.get_parameter('soggetto_attuatore__slug', sogg_attuatore_set,
                                                                   model=SoggettoAttuatore)

        sogg_attuatore_tipologia_set = SoggettoAttuatore.TIPOLOGIA._db_values
        sogg_att_tipologia_slug = self.get_parameter('soggetto_attuatore__tipologia', sogg_attuatore_tipologia_set)
        if sogg_att_tipologia_slug is not None and sogg_att_tipologia_slug is not False:
            self.filters['sogg_attuatore_tipologia_filter'] = SoggettoAttuatore.TIPOLOGIA._display_map[
                sogg_att_tipologia_slug]

        #status filters
        bool_set = [u'True', u'False']
        self.filters['a_piano_filter'] = self.get_parameter('a_piano', bool_set)
        self.filters['in_attuazione_filter'] = self.get_parameter('in_attuazione', bool_set)

        stato_attuazione_set = list(InterventoProgramma.STATO_ATTUAZIONE._db_values)
        self.filters['stato_attuazione_filter'] = self.get_parameter('stato_attuazione', stato_attuazione_set)

        impresa_set = Impresa.objects.all().values_list('slug', flat=True)
        self.filters['impresa_filter'] = self.get_parameter('interventopiano__intervento__imprese__slug', impresa_set,
                                                            model=Impresa)


class AggregatePageMixin(object):
    ##
    # Aggregati Page Mixin
    # stores the common function of all the aggregate views
    ##

    programmazione_filters = None
    varianti_filters = {}
    imprese_filters = {}
    sogg_att_filters = None
    donazione_intervento_filters = {}
    tipologia = None

    TERRITORIO = 0
    VARI_TERRITORI = 1
    TIPO_IMMOBILE = 2
    SOGG_ATT = 3
    HOME = 4
    IMPRESA = 5

    def __init__(self, tipologia, programmazione_filters, sogg_att_filters):
        ##
        # initialize class with type and filter for programmazione / pianificazione
        ##

        self.tipologia = tipologia
        self.programmazione_filters = programmazione_filters

        # transforms programmazione filters into donazioneIntervento filters
        for k, v in programmazione_filters.iteritems():
            self.donazione_intervento_filters["intervento_programma__{}".format(k)] = v
            self.imprese_filters["intervento__intervento_piano__intervento_programma__{}".format(k)] = v
            self.varianti_filters["intervento__intervento_piano__intervento_programma__{}".format(k)] = v

        self.sogg_att_filters = sogg_att_filters

    def _get_aggr_donazioni(self, ):
        values = []
        # get aggr donazioni uses programmazione filters because it's used only for home page: no filters or
        # territorio page: only territorio filters

        for tipologia in Donazione.TIPO_CEDENTE:
            d = {'name': tipologia[1], 'tipologia': tipologia}
            d.update(Donazione.get_aggregates(tipologia=tipologia, **self.programmazione_filters))
            values.append(d)

        return values

    def _get_totale_donazioni(self):
        return Donazione.get_aggregates(tipologia=None, **self.programmazione_filters)

    def _get_totale_donazioni_interventi(self):
        return DonazioneInterventoProgramma.get_aggregates(**self.donazione_intervento_filters)

    def _get_aggr_donazioni_interventi(self):
        values = []

        for tipologia in Donazione.TIPO_CEDENTE:
            d = {'name': tipologia[1]}
            d.update(DonazioneInterventoProgramma.get_aggregates(donazione__tipologia_cedente=tipologia[0],
                                                                 **self.donazione_intervento_filters))
            values.append(d)

        return values

    def fetch_top_interventi_attuazione(self, ):
        n_objects = settings.N_PROGETTI_FETCH
        order_by = '-interventopiano__intervento__imp_consolidato'
        return list(
            InterventoProgramma.attuazione.filter(**self.programmazione_filters).order_by(order_by)[0:n_objects])

    def fetch_imprese(self, ):
        n_objects = settings.N_IMPRESE_FETCH
        return list(
            Impresa.objects.filter(**self.imprese_filters).annotate(
                count=Count('intervento__intervento_piano__intervento_programma')).order_by('-count')[0:n_objects])

    def fetch_sogg_att(self):
        n_objects = settings.N_SOGG_ATT_FETCH
        return list(
            SoggettoAttuatore.objects.
            filter(**self.sogg_att_filters).
            annotate(Count('interventoprogramma')).
            order_by('-interventoprogramma__count').
            values('denominazione', 'interventoprogramma__count', 'slug')[0:n_objects]
        )

    def _get_programmazione_status(self):
        return InterventoProgramma.programmati.filter(**self.programmazione_filters).with_count()

    def _get_pianificazione_status(self):
        return InterventoProgramma.pianificati.filter(**self.programmazione_filters).with_count()

    def _get_attuazione_status(self):
        return InterventoProgramma.attuazione.filter(**self.programmazione_filters).with_count()

    def _get_varianti_status(self):
        return Variante.objects.filter(**self.varianti_filters).with_count()

    def _get_progettazione_status(self):
        return InterventoProgramma.progettazione.filter(**self.programmazione_filters).with_count()

    def _get_in_corso_status(self):
        return InterventoProgramma.in_corso.filter(**self.programmazione_filters).with_count()

    def _get_conclusi_status(self):
        return InterventoProgramma.conclusi.filter(**self.programmazione_filters).with_count()

    def get_base_filters(self):
        if self.tipologia == self.TERRITORIO:
            return 'territorio__slug={}'.format(self.programmazione_filters['territorio'].slug)
        if self.tipologia == self.VARI_TERRITORI:
            return 'vari_territori=True'
        elif self.tipologia == self.SOGG_ATT:
            return 'soggetto_attuatore__slug={}'.format(self.programmazione_filters['soggetto_attuatore'].slug)
        elif self.tipologia == self.TIPO_IMMOBILE:
            return 'tipo_immobile__slug={}'.format(self.programmazione_filters['tipo_immobile'].slug)
        elif self.tipologia == self.IMPRESA:
            return 'interventopiano__intervento__imprese__slug={}'.format(
                self.programmazione_filters['interventopiano__intervento__imprese'].slug)

    def get_aggregates(self):
        ##
        # calls the functions to get the aggregates and returns a dict
        # all the function called depend on the filters passed to AggregatePageMixin on initialization
        # so they return context-based data
        ##

        agg_dict = {
            'status': {
                'programmazione': self._get_programmazione_status(),
                'pianificazione': self._get_pianificazione_status(),
                'attuazione': self._get_attuazione_status(),
                'varianti': self._get_varianti_status(),
                'progettazione': self._get_progettazione_status(),
                'in_corso': self._get_in_corso_status(),
                'conclusi': self._get_conclusi_status(),
            },
            'total_percentage': {
                'programmazione': 0,
                'pianificazione': 0,
                'attuazione': 0,
            }
        }

        # calculates percentages of programmazione / pianificazione / attuazione compared to the whole of projects
        agg_dict['total_percentage']['programmazione'] = (agg_dict['status']['programmazione']['sum'] /
                                                          InterventoProgramma.programmati.all().with_count()[
                                                              'sum']) * Decimal(100.0)
        agg_dict['total_percentage']['pianificazione'] = (agg_dict['status']['pianificazione']['sum'] /
                                                          InterventoProgramma.pianificati.all().with_count()[
                                                              'sum']) * Decimal(100.0)
        agg_dict['total_percentage']['attuazione'] = (agg_dict['status']['attuazione']['sum'] /
                                                      InterventoProgramma.attuazione.all().with_count()[
                                                          'sum']) * Decimal(100.0)

        agg_dict['total_percentage']['programmazione'] = "{0:.2f}".format(
            agg_dict['total_percentage']['programmazione'])
        agg_dict['total_percentage']['pianificazione'] = "{0:.2f}".format(
            agg_dict['total_percentage']['pianificazione'])
        agg_dict['total_percentage']['attuazione'] = "{0:.2f}".format(agg_dict['total_percentage']['attuazione'])


        # calculate percentages of pianificazione / attuazione / varianti based on current filters
        agg_dict['status']['pianificazione']['percentage'] = 0.0
        agg_dict['status']['attuazione']['percentage'] = 0.0
        agg_dict['status']['varianti']['percentage'] = 0.0

        if agg_dict['status']['programmazione']['sum'] > 0 and agg_dict['status']['pianificazione']['sum'] > 0:
            agg_dict['status']['pianificazione']['percentage'] = Decimal(100.0) * (
                agg_dict['status']['pianificazione']['sum'] /
                agg_dict['status']['programmazione']['sum'])

            if agg_dict['status']['attuazione']['sum']:
                agg_dict['status']['attuazione']['percentage'] = Decimal(100.0) * (
                    agg_dict['status']['attuazione']['sum'] /
                    agg_dict['status']['programmazione']['sum'])

        # calculates % in varianti compared to attuazione importo
        if agg_dict['status']['attuazione']['sum'] > 0 and agg_dict['status']['varianti']['sum']:
            agg_dict['status']['varianti']['percentage'] = Decimal(100.0) * (
                agg_dict['status']['varianti']['sum'] /
                agg_dict['status']['attuazione']['sum'])

        # top importo interventi fetch
        agg_dict['interventi_top_importo'] = self.fetch_top_interventi_attuazione()

        # Get tipo immobile pie data
        if self.tipologia != self.TIPO_IMMOBILE:
            agg_dict['tipo_immobile_aggregates'] = InterventoProgramma.get_tipo_immobile_aggregates(
                **self.programmazione_filters)

        if self.tipologia != self.IMPRESA:
            agg_dict['imprese_top'] = self.fetch_imprese()

        # Get tipo sogg.att data
        if self.tipologia != self.SOGG_ATT and self.tipologia != self.IMPRESA:
            agg_dict['sogg_att_aggregates'] = InterventoProgramma.get_sogg_attuatore_aggregates(
                **self.programmazione_filters)
            agg_dict['sogg_att_top'] = self.fetch_sogg_att()

        # Get donazioni data

        # if home or localita page: use programmazione filters ( no filters or territorio filters)
        # else (tipo immobile) use DonazioneInterventoProgramma filters
        if self.tipologia == self.HOME or self.tipologia == self.TERRITORIO:
            agg_dict['donazioni_aggregates'] = self._get_aggr_donazioni()
            agg_dict['donazioni_totale'] = self._get_totale_donazioni()
        else:
            agg_dict['donazioni_aggregates'] = self._get_aggr_donazioni_interventi()
            agg_dict['donazioni_totale'] = self._get_totale_donazioni_interventi()

        return agg_dict


class LocalitaView(TemplateView, AggregatePageMixin, LocalitaMapMixin):
    template_name = 'localita.html'
    territorio = None
    vari_territori = False
    interventi_programma = None

    def get(self, request, *args, **kwargs):
        # get data from the request
        if kwargs['slug'] == 'vari-territori':
            self.vari_territori = True
        else:
            try:
                self.territorio = Territorio.objects.get(slug=kwargs['slug'])
            except ObjectDoesNotExist:
                return HttpResponseRedirect(reverse('404'))
        return super(LocalitaView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(LocalitaView, self).get_context_data(**kwargs)
        context['territorio'] = self.territorio
        context['vari_territori'] = self.vari_territori

        if self.vari_territori:
            apm = AggregatePageMixin(
                tipologia=AggregatePageMixin.VARI_TERRITORI,
                programmazione_filters={'vari_territori': True},
                sogg_att_filters={'interventoprogramma__vari_territori': True}
            )
        else:
            apm = AggregatePageMixin(
                tipologia=AggregatePageMixin.TERRITORIO,
                programmazione_filters={'territorio': self.territorio},
                sogg_att_filters={'interventoprogramma__territorio__slug': self.territorio.slug}
            )
            self.interventi_programma = InterventoProgramma.objects.filter(territorio=self.territorio)

        context.update(apm.get_aggregates())
        context['base_filters'] = apm.get_base_filters()

        if self.vari_territori is False:
            # calculate the map bounds for the territorio
            map_data = self.get_map_data
            context['map_bounds'] = map_data['map_bounds']
            context['map_center'] = map_data['map_center']
            context['map_pois'] = map_data['map_pois']

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
            sogg_att_filters={'interventoprogramma__tipo_immobile': self.tipo_immobile}
        )
        context.update(apm.get_aggregates())
        context['base_filters'] = apm.get_base_filters()
        # gets maps bounds and center
        context['map_bounds'] = settings.THEMATIC_MAP_BOUNDS
        context['map_center'] = settings.THEMATIC_MAP_CENTER
        # get maps data
        mapm = ThematicMapMixin(map_filters={'interventoprogramma__tipo_immobile': self.tipo_immobile})
        context['map_danno_values'] = mapm.get_danno_values('tipo_immobile')
        context['map_attuazione_values'] = mapm.get_attuazione_values('tipo_immobile')

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
            sogg_att_filters={}
        )
        context.update(apm.get_aggregates())
        context['base_filters'] = apm.get_base_filters()

        # gets maps bounds and center
        context['map_bounds'] = settings.THEMATIC_MAP_BOUNDS
        context['map_center'] = settings.THEMATIC_MAP_CENTER
        # get maps data
        mapm = ThematicMapMixin(map_filters={'interventoprogramma__soggetto_attuatore': self.sogg_att})
        context['map_danno_values'] = mapm.get_danno_values('soggetto_attuatore')
        context['map_attuazione_values'] = mapm.get_attuazione_values('soggetto_attuatore')

        return context


class HomeView(TemplateView, AggregatePageMixin, ThematicMapMixin):
    template_name = "home.html"


    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        apm = AggregatePageMixin(
            tipologia=AggregatePageMixin.HOME,
            programmazione_filters={},
            sogg_att_filters={}
        )
        context.update(apm.get_aggregates())


        # gets maps bounds and center
        context['map_bounds'] = settings.THEMATIC_MAP_BOUNDS
        context['map_center'] = settings.THEMATIC_MAP_CENTER
        mapm = ThematicMapMixin(map_filters={})

        context['map_danno_values'] = mapm.get_danno_values("home")
        context['map_attuazione_values'] = mapm.get_attuazione_values("home")

        return context


class TipoSoggettoAttuatoreView(ListView):
    template_name = 'sogg_att_list.html'
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
        return SoggettoAttuatore.objects.filter(tipologia=self.tipologia_sogg_att).annotate(
            count=Count('interventoprogramma')).annotate(sum=Sum('interventoprogramma__importo_generale'))

    def get_context_data(self, **kwargs):
        context = super(TipoSoggettoAttuatoreView, self).get_context_data(**kwargs)
        context['tipologia_sogg_att'] = SoggettoAttuatore.TIPOLOGIA[self.tipologia_sogg_att]
        return context


class ImpreseListView(ListView):
    template_name = 'imprese_list.html'

    def get_queryset(self):
        return Impresa.objects.all().order_by('ragione_sociale')


class InterventoProgrammaView(DetailView, InterventoProgrammaMapMixin):
    model = InterventoProgramma
    template_name = 'intervento_programma.html'
    territorio = None
    intervento_programma = None
    intervento_piano = None
    intervento = None
    imprese = None
    progetti = None
    eventi_in_corso = None
    evento_fine = None
    varianti = None
    cofinanziamenti = None
    liquidazioni = None
    importo_liquidazioni = None

    def get(self, request, *args, **kwargs):
        # get data from the request

        try:
            self.intervento_programma = InterventoProgramma.objects.get(slug=kwargs['slug'])
        except ObjectDoesNotExist:
            return HttpResponseRedirect(reverse('404'))
        else:

            self.cofinanziamenti = Cofinanziamento.objects.filter(
                intervento_programma=self.intervento_programma).order_by('tipologia')
            try:
                self.intervento_piano = InterventoPiano.objects.get(intervento_programma=self.intervento_programma)
            except ObjectDoesNotExist:
                pass
            else:
                try:
                    self.intervento = Intervento.objects.get(intervento_piano=self.intervento_piano)
                except ObjectDoesNotExist:
                    pass
                else:
                    self.imprese = self.intervento.imprese.all()
                    self.varianti = Variante.objects.filter(intervento=self.intervento)
                    self.liquidazioni = Liquidazione.objects.filter(intervento=self.intervento).order_by('data')
                    if self.liquidazioni:
                        self.importo_liquidazioni = self.liquidazioni.aggregate(s=Sum('importo'))['s']
                    self.progetti = Progetto.objects.filter(intervento=self.intervento).order_by('data_inizio',
                                                                                                 'data_deposito',
                                                                                                 'data_fine')
                    self.eventi_in_corso = EventoContrattuale.objects.filter(intervento=self.intervento).exclude(
                        tipologia=EventoContrattuale.TIPO_EVENTO.FINE_LAVORI_CERTIFICATO).order_by('data')
                    try:
                        self.evento_fine = EventoContrattuale.objects.get(intervento=self.intervento,
                                                                          tipologia=EventoContrattuale.TIPO_EVENTO.FINE_LAVORI_CERTIFICATO)
                    except ObjectDoesNotExist:
                        pass

        return super(InterventoProgrammaView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(InterventoProgrammaView, self).get_context_data(**kwargs)
        # transfer to context the context variables about the interv.programma
        context['intervento_programma'] = self.intervento_programma
        context['intervento_piano'] = self.intervento_piano
        context['intervento'] = self.intervento
        context['varianti'] = self.varianti
        context['liquidazioni'] = self.liquidazioni
        context['imprese'] = self.imprese
        context['progetti'] = self.progetti
        context['eventi_in_corso'] = self.eventi_in_corso
        context['evento_fine'] = self.evento_fine

        importo = 0
        if self.intervento_programma.stato == InterventoProgramma.STATO.PROGRAMMA:
            importo = self.intervento_programma.importo_generale
        elif self.intervento_programma.stato == InterventoProgramma.STATO.PIANO:
            importo = self.intervento_piano.imp_consolidato
        elif self.intervento_programma.stato == InterventoProgramma.STATO.ATTUAZIONE:
            importo = self.intervento.imp_consolidato

        context['importo'] = importo
        context['importo_liquidazioni'] = self.importo_liquidazioni

        context[
            'importo_cofinanziamenti'] = self.intervento_programma.importo_generale - self.intervento_programma.importo_a_programma
        context['cofinanziamenti'] = self.cofinanziamenti

        self.territorio = self.intervento_programma.territorio
        if self.intervento_programma.vari_territori is False:
            # calculate the map bounds for the territorio
            data_map = self.get_map_data()
            context['map_bounds'] = data_map['map_bounds']
            context['map_center'] = data_map['map_center']
            context['map_tooltip_text'] = self.intervento_programma.denominazione
            context['territorio'] = self.territorio

        return context


class ImpresaDetailView(DetailView, AggregatePageMixin):
    model = Impresa
    template_name = 'impresa.html'
    impresa = None

    def get(self, request, *args, **kwargs):
        # get data from the request
        try:
            self.impresa = Impresa.objects.get(slug=kwargs['slug'])
        except ObjectDoesNotExist:
            return HttpResponseRedirect(reverse('404'))
        return super(ImpresaDetailView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ImpresaDetailView, self).get_context_data(**kwargs)
        context['impresa'] = self.impresa

        apm = AggregatePageMixin(
            tipologia=AggregatePageMixin.IMPRESA,
            programmazione_filters={"interventopiano__intervento__imprese": self.impresa},
            sogg_att_filters={}
        )
        context.update(apm.get_aggregates())
        context['base_filters'] = apm.get_base_filters()
        # gets maps bounds and center
        context['map_bounds'] = settings.THEMATIC_MAP_BOUNDS
        context['map_center'] = settings.THEMATIC_MAP_CENTER
        # get maps data
        mapm = ThematicMapMixin(map_filters={'interventoprogramma__interventopiano__intervento__imprese': self.impresa})
        context['map_attuazione_values'] = mapm.get_attuazione_values('impresa')

        return context


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

        try:
            url = reverse('intervento-programma', args=args, kwargs=kwargs)
        except NoReverseMatch:
            return reverse('404')

        return url


class ImpresaRedirectView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):

        # get impresa data from the request
        try:
            impresa = get_object_or_404(Impresa, slug=self.request.GET.get('impresa', 0))
        except Http404:
            return reverse('404')

        kwargs.update({'slug': impresa.slug})

        try:
            url = reverse('impresa', args=args, kwargs=kwargs)
        except NoReverseMatch:
            return reverse('404')

        return url