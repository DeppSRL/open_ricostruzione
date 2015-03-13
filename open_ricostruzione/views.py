from decimal import Decimal
import datetime
from datetime import timedelta
import json
from json.encoder import JSONEncoder
import time
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, Http404
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView, DetailView, ListView
from django.db.models.aggregates import Count, Sum
from django.conf import settings
from rest_framework import generics
from django.db import connections
from django.db.models.query import QuerySet
from django.core.serializers import serialize
from django.utils.functional import curry
from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.defaultfilters import date as _date
from open_ricostruzione.models import InterventoProgramma, Donazione, InterventoPiano, TipoImmobile, SoggettoAttuatore
from territori.models import Territorio
from .serializers import DonazioneSerializer
from open_ricostruzione.utils.moneydate import moneyfmt, add_months


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

    @staticmethod
    def get_aggr_tipologia_cedente():
        values = []
        for k, v in Donazione.get_aggregates_sum().iteritems():
            if v:
                v = float(v)
            else:
                v = 0.0

            values.append({'value': v, 'slug': k, 'label': Donazione.TIPO_CEDENTE.__getitem__(k)})

        return values

    @staticmethod
    def _create_aggregate_int_progr(model):
        ##
        # creates the list of dict to be passed to the context.
        # calls the appropriate model function to get sums of the various categories of objects
        ##

        values = []
        for k, v in InterventoProgramma.get_aggregates_sum(model).iteritems():
            if v:
                v = float(v)
            else:
                v = 0.0

            values.append({'value': v, 'slug': k, 'label': model.TIPOLOGIA.__getitem__(k)})

        return values

    @staticmethod
    def get_aggr_tipo_immobile():
        return AggregatePageMixin._create_aggregate_int_progr(TipoImmobile)

    @staticmethod
    def get_aggr_sogg_att():
        return AggregatePageMixin._create_aggregate_int_progr(SoggettoAttuatore)


    @staticmethod
    def fetch_interventi_programma(order_by, number):
        return InterventoProgramma.objects.all().order_by(order_by)[0:number]

    @staticmethod
    def get_ricostruzione_status():
        ricostruzione_status = {
            'piano': {},
            'programma': {},
            'attuazione': {},
        }
        ricostruzione_status['programma']['count'] = InterventoProgramma.objects.all().count()
        ricostruzione_status['piano']['count'] = InterventoPiano.objects.all().count()
        ricostruzione_status['programma']['money_value'] = \
            InterventoProgramma.objects.all().aggregate(Sum('importo_generale'))['importo_generale__sum']
        ricostruzione_status['piano']['money_value'] = InterventoPiano.objects.all().aggregate(Sum('imp_a_piano'))[
            'imp_a_piano__sum']
        ricostruzione_status['piano']['percentage'] = 100.0 * (
            ricostruzione_status['piano']['count'] / float(ricostruzione_status['programma']['count']))

        # todo: aggiugnere la parte sull'attuazione

        return ricostruzione_status


class HomeView(TemplateView, AggregatePageMixin):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)

        context['ricostruzione_status'] = AggregatePageMixin.get_ricostruzione_status()

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


class LocalitaView(DetailView):
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
