from django.views.generic import TemplateView, DetailView
from django.db.models.aggregates import Count, Sum
from open_ricostruzione.models import *
from django.db import connections
import locale
from datetime import datetime
import time


class HomeView(TemplateView):
    template_name = "home.html"

class ProgettoView(DetailView):
    model = Progetto
    context_object_name = "progetto"
    template_name = 'progetto.html'

    def get_context_data(self, **kwargs ):
        p = self.get_object()
        context = super(ProgettoView, self).get_context_data(**kwargs)

        context['territorio_nome'] = p.territorio.denominazione
        iban =  Progetto.objects.get(pk = p.pk).territorio.iban
        if iban:
            context['iban'] = iban

#        mancano le donazioni perche' ci mancano i le relazioni fra donazioni e progetti

        return context

class TerritorioView(DetailView):
    model = Territorio
    context_object_name = "territorio"
    template_name = 'territorio.html'

    def get_context_data(self, **kwargs ):
        t = self.get_object()
        context = super(TerritorioView, self).get_context_data(**kwargs)

        # importi progetti totale
        tot_progetti = Progetto.objects.filter(territorio=t).aggregate(s=Sum('riepilogo_importi')).values()

        # donazioni per il territorio considerato
        tot_donazioni = Donazione.objects.filter(territorio=t).aggregate(s=Sum('importo')).values()
        if tot_donazioni:
            context['tot_donazioni']= tot_donazioni
            context['donazioni'] = Donazione.objects.filter(territorio=t)

        # importi dei progetti per categorie
        context['progetti_categorie'] =  \
            Progetto.objects.filter(territorio=t).values('tipologia').\
            annotate(somma_categoria=Sum('riepilogo_importi'))

        # donazioni divise per tipologia cedente
        context['donazioni_categorie'] = \
            Donazione.objects.filter( territorio=t).\
            filter(confermato = True).values('tipologia').\
            annotate(somma_categoria = Sum('importo'))

        #iban territorio
        iban = Territorio.objects.get(pk = t.pk).iban
        if iban:
            context['iban'] = iban

        #lista progetti per questo territorio in ordine di costo decrescente
        projects = Progetto.objects.filter(territorio = t).order_by('-riepilogo_importi')[:10]

        if projects:
            context['projects'] = projects

        return context

class DonazioneView(TemplateView):

    template_name = "donazioni.html"


    def get_context_data(self, **kwargs):
        context = super(DonazioneView, self).get_context_data(**kwargs)

        # donazioni totali
        tot_donazioni = Donazione.objects.all().aggregate(s=Sum('importo')).values()
        if tot_donazioni:
            context['tot_donazioni']= tot_donazioni

        # importi progetti totale
        tot_progetti = Progetto.objects.all().aggregate(s=Sum('riepilogo_importi')).values()
        if tot_progetti:
            context['tot_progetti'] = tot_progetti

        #tutte le donazioni nel tempo
        #le donazioni vengono espresse con valori incrementali rispetto alla somma delle donazioni
        # del mese precedente. In questo modo se un mese le donazioni sono 0 la retta del grafico e' piatta

        donazioni = Donazione.objects.\
                        extra(select={'month': connections[Donazione.objects.db].ops.date_trunc_sql('month', 'data')}).\
                        values('month').annotate(d_sum = Sum('importo'))

        for idx, val in enumerate(donazioni):
#            converto la data nel formato  Nome mese - Anno
            date_obj = datetime.strptime(val['month'],"%Y-%m-%d %H:%M:%S")
            val['month']= time.strftime("%b - %Y", date_obj.timetuple())

            if idx is not 0:
                val['d_sum'] = (donazioni[idx-1]['d_sum']+ abs(val['d_sum'] - donazioni[idx-1]['d_sum']))




        if donazioni:
            context['donazioni'] = donazioni
#            context['donazioni_first'] = donazioni[0].data
            n_donazioni = donazioni.count()
#            context['donazioni_last'] = donazioni[n_donazioni-1].data

        #donazioni per categoria

        context['donazioni_tipologia'] =\
            Donazione.objects.all().filter(confermato=True).values('tipologia').\
            annotate(count=Count('tipologia')).annotate(somma = Sum('importo')).\
            order_by('tipologia')

        return context