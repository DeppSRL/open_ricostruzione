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


class AggregatePageMixin(object):
    ##
    # Aggregati Page Mixin
    # stores the common function of all the aggregate views
    ##

    def get_programmati_pianificati(self):
        return

    @staticmethod
    def _create_aggregate_data(model):
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
        return AggregatePageMixin._create_aggregate_data(TipoImmobile)

    @staticmethod
    def get_aggr_sogg_att():
        return AggregatePageMixin._create_aggregate_data(SoggettoAttuatore)


    @staticmethod
    def fetch_interventi_programma(order_by, number):
        return InterventoProgramma.objects.all().order_by(order_by)[0:number]


class HomeView(TemplateView, AggregatePageMixin):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)

        n_int_programma = InterventoProgramma.objects.count()
        n_int_piano = InterventoPiano.objects.count()
        context['importo_int_programma'] = InterventoProgramma.objects.all().aggregate(Sum('importo_generale'))[
            'importo_generale__sum']
        context['importo_int_piano'] = InterventoPiano.objects.all().aggregate(Sum('imp_a_piano'))['imp_a_piano__sum']
        context['perc_a_piano'] = 100.0 * (n_int_piano / float(n_int_programma))
        context['n_int_programma'] = n_int_programma
        context['n_int_piano'] = n_int_piano

        # tipo immobile pie data
        context['tipo_immobile_aggregates_sum'] = AggregatePageMixin.get_aggr_tipo_immobile()

        context['sogg_att_aggregates_sum'] = AggregatePageMixin.get_aggr_sogg_att()

        # example interventi fetch
        interventi_top_importo = AggregatePageMixin.fetch_interventi_programma('-importo_generale',5)
        interventi_bottom_importo = AggregatePageMixin.fetch_interventi_programma('importo_generale',5)

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
