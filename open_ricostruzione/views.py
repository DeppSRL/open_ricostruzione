from django.core.exceptions import ObjectDoesNotExist
from django.http.response import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse, NoReverseMatch
from django.shortcuts import get_object_or_404, render_to_response
from django.views.generic import TemplateView, DetailView, ListView, RedirectView
from django.db.models.aggregates import Count, Sum
from django_filters.views import FilterView
from django.conf import settings
from open_ricostruzione.models import InterventoProgramma, Donazione, TipoImmobile, SoggettoAttuatore, Impresa, DonazioneInterventoProgramma
from territori.models import Territorio
from open_ricostruzione.utils import convert2dict
from open_ricostruzione.filters import InterventoProgrammaFilter


class PageNotFoundTemplateView(TemplateView):
    template_name = '404.html'


class StaticPageView(TemplateView, ):
    template_name = 'static_page.html'


class ListaInterventiView(FilterView):
    template_name = 'interventi_list.html'
    model = InterventoProgramma
    request = None

    def get(self, request, *args, **kwargs):
        self.request = request
        return super(ListaInterventiView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ListaInterventiView, self).get_context_data(**kwargs)
        ip_filter = InterventoProgrammaFilter(self.request.GET,
                                              queryset=InterventoProgramma.objects.all().select_related('territorio'))
        context['filter'] = ip_filter
        territorio_slug = ip_filter.form.data.get('territorio__slug', None)

        if territorio_slug:
            context['territorio_filter'] = Territorio.objects.get(slug=territorio_slug)

        tipo_immobile_slug = ip_filter.form.data.get('tipo_immobile__slug', None)
        if tipo_immobile_slug:
            context['tipo_immobile_filter'] = TipoImmobile.objects.get(slug=tipo_immobile_slug)

        sogg_attuatore_slug = ip_filter.form.data.get('soggetto_attuatore__slug', None)
        if sogg_attuatore_slug:
            context['sogg_attuatore_filter'] = SoggettoAttuatore.objects.get(slug=sogg_attuatore_slug)

        context['stato_filter'] = ip_filter.form.data.get('stato', None)
        context['stato_attuazione_filter'] = ip_filter.form.data.get('stato_attuazione', None)


        context['request'] = self.request
        return context


class DonazioniListView(ListView):
    paginate_by = 100
    model = Donazione
    template_name = 'donazioni_list.html'

    def get_queryset(self):
        queryset = super(DonazioniListView, self).get_queryset()
        return queryset.select_related('territorio')


class AggregatePageMixin(object):
    ##
    # Aggregati Page Mixin
    # stores the common function of all the aggregate views
    ##

    programmazione_filters = None
    sogg_att_filters = None
    donazione_intervento_filters = {}
    tipologia = None

    TERRITORIO = 0
    VARI_TERRITORI = 1
    TIPO_IMMOBILE = 2
    SOGG_ATT = 3
    HOME = 4

    def __init__(self, tipologia, programmazione_filters, sogg_att_filters):
        ##
        # initialize class with type and filter for programmazione / pianificazione
        ##

        self.tipologia = tipologia
        self.programmazione_filters = programmazione_filters

        # transforms programmazione filters into donazioneIntervento filters
        for k, v in programmazione_filters.iteritems():
            self.donazione_intervento_filters["intervento_programma__{}".format(k)] = v

        self.sogg_att_filters = sogg_att_filters

    def _get_aggr_donazioni(self, ):
        values = []
        # get aggr donazioni uses programmazione filters because it's used only for home page: no filters or
        # territorio page: only territorio filters

        for tipologia in Donazione.TIPO_CEDENTE:
            d = {'name': tipologia[1]}
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
            d.update(
                DonazioneInterventoProgramma.get_aggregates(tipologia=tipologia, **self.donazione_intervento_filters))
            values.append(d)

        return values

    def fetch_interventi_programma(self, order_by, ):
        n_objects = settings.N_PROGETTI_FETCH
        return list(InterventoProgramma.objects.filter(**self.programmazione_filters).order_by(order_by)[0:n_objects])

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

    def _get_progettazione_status(self):
        return InterventoProgramma.progettazione.filter(**self.programmazione_filters).with_count()

    def _get_in_corso_status(self):
        return InterventoProgramma.in_corso.filter(**self.programmazione_filters).with_count()

    def _get_conclusi_status(self):
        return InterventoProgramma.conclusi.filter(**self.programmazione_filters).with_count()

    def get_base_filters(self):
        if self.tipologia == self.TERRITORIO:
            return 'territorio__slug={}'.format(self.programmazione_filters['territorio'].slug)

    def get_aggregates(self):
        ##
        # calls the functions to get the aggregates and returns a dict
        # all the function called depend on the filters passed to AggregatePageMixin on initialization
        # so they return context-based data
        ##

        agg_dict = {'status': {
            'programmazione': self._get_programmazione_status(),
            'pianificazione': self._get_pianificazione_status(),
            'attuazione': self._get_attuazione_status(),
            'progettazione': self._get_progettazione_status(),
            'in_corso': self._get_in_corso_status(),
            'conclusi': self._get_conclusi_status(),
        }}

        agg_dict['status']['pianificazione']['percentage'] = 0.0
        agg_dict['status']['attuazione']['percentage'] = 0.0

        if agg_dict['status']['programmazione']['count'] > 0:
            agg_dict['status']['pianificazione']['percentage'] = 100.0 * (
                agg_dict['status']['pianificazione']['count'] / float(
                    agg_dict['status']['programmazione']['count']))

            agg_dict['status']['attuazione']['percentage'] = 100.0 * (
                agg_dict['status']['attuazione']['count'] / float(
                    agg_dict['status']['programmazione']['count']))

        # top importo interventi fetch
        agg_dict['interventi_top_importo'] = self.fetch_interventi_programma(order_by='-importo_generale')

        # Get tipo immobile pie data
        if self.tipologia != self.TIPO_IMMOBILE:
            agg_dict['tipo_immobile_aggregates'] = InterventoProgramma.get_tipo_immobile_aggregates(
                **self.programmazione_filters)

        # Get tipo sogg.att data
        if self.tipologia != self.SOGG_ATT:
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
                sogg_att_filters={'interventoprogramma__vari_territori': True}
            )
        else:
            apm = AggregatePageMixin(
                tipologia=AggregatePageMixin.TERRITORIO,
                programmazione_filters={'territorio': self.territorio},
                sogg_att_filters={'interventoprogramma__territorio__slug': self.territorio.slug}
            )

        context.update(apm.get_aggregates())

        if self.vari_territori is False:
            # calculate the map bounds for the territorio
            bounds_width = settings.LOCALITA_MAP_BOUNDS_WIDTH
            context['base_filters'] = apm.get_base_filters()

            context['map_bounds'] = \
                {'sw':
                     {'lat': self.territorio.gps_lat - bounds_width,
                      'lon': self.territorio.gps_lon - bounds_width,
                     },
                 'ne':
                     {'lat': self.territorio.gps_lat + bounds_width,
                      'lon': self.territorio.gps_lon + bounds_width,
                     },
                }

        return context


class MapMixin(object):
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
        for t in MapMixin._get_territorio_set():
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

    def get_danno_values(self):

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

        return MapMixin._create_map_values(danno_values)

    def get_attuazione_values(self):

        attuazione_values = list(
            Territorio.objects.filter(tipologia="C", regione="Emilia Romagna"). \
                filter(**self.map_filters). \
                annotate(Sum('interventoprogramma__interventopiano__intervento__imp_congr_spesa')). \
                annotate(Sum('interventoprogramma__importo_generale')). \
                values('slug',
                       'interventoprogramma__interventopiano__intervento__imp_congr_spesa__sum',
                       'interventoprogramma__importo_generale__sum'))

        print self.map_filters
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
            valore_attuaz = item['interventoprogramma__interventopiano__intervento__imp_congr_spesa__sum']
            item['sum'] = valore_attuaz
            valore_progr = item['interventoprogramma__importo_generale__sum']

            # add count of interventi in attuazione
            if n_interventi_dict.get(item['slug'], None):
                item['count'] = n_interventi_dict[item['slug']][0]['c']

            if valore_progr and valore_progr != 0 and valore_attuaz:
                item['value'] = 100.0 * float(valore_attuaz / valore_progr)

        return MapMixin._create_map_values(attuazione_values)


class TipoImmobileView(TemplateView, AggregatePageMixin, MapMixin):
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

        # gets maps bounds and center
        context['map_bounds'] = settings.THEMATIC_MAP_BOUNDS
        context['map_center'] = settings.THEMATIC_MAP_CENTER
        # get maps data
        mapm = MapMixin(map_filters={'interventoprogramma__tipo_immobile': self.tipo_immobile})
        context['map_danno_values'] = mapm.get_danno_values()
        context['map_attuazione_values'] = mapm.get_attuazione_values()

        return context


class SoggettoAttuatoreView(TemplateView, AggregatePageMixin, MapMixin):
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

        # gets maps bounds and center
        context['map_bounds'] = settings.THEMATIC_MAP_BOUNDS
        context['map_center'] = settings.THEMATIC_MAP_CENTER
        # get maps data
        mapm = MapMixin(map_filters={'interventoprogramma__soggetto_attuatore': self.sogg_att})
        context['map_danno_values'] = mapm.get_danno_values()
        context['map_attuazione_values'] = mapm.get_attuazione_values()

        return context


class HomeView(TemplateView, AggregatePageMixin, MapMixin):
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
        # get maps data
        mapm = MapMixin(map_filters={})
        context['map_danno_values'] = mapm.get_danno_values()
        context['map_attuazione_values'] = mapm.get_attuazione_values()

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


class ImpresaDetailView(DetailView):
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

        # gets maps bounds and center
        context['map_bounds'] = settings.THEMATIC_MAP_BOUNDS
        context['map_center'] = settings.THEMATIC_MAP_CENTER
        # get maps data
        mapm = MapMixin(map_filters={'interventoprogramma__interventopiano__intervento__imprese': self.impresa})
        context['map_attuazione_values'] = mapm.get_attuazione_values()

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