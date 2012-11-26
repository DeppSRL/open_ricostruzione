from django.views.generic import TemplateView, DetailView
from django.db.models.aggregates import Count, Sum
from open_ricostruzione.models import *

class HomeView(TemplateView):
    template_name = "home.html"

class ProgettoView(DetailView):
    model = Progetto
    context_object_name = "progetto"
    template_name = 'progetto.html'

    def get_context_data(self, **kwargs ):
        p = self.get_object()
        context = super(ProgettoView, self).get_context_data(**kwargs)

        context['comune_nome'] = p.comune.denominazione
        iban_comune =  Progetto.objects.get(pk = p.pk).comune.iban
        if iban_comune:
            context['iban'] = iban_comune

#        mancano le donazioni perche' ci mancano i le relazioni fra donazioni e progetti

        return context

class ComuneView(DetailView):
    model = Comune
    context_object_name = "comune"
    template_name = 'comune.html'

    def get_context_data(self, **kwargs ):
        c = self.get_object()
        context = super(ComuneView, self).get_context_data(**kwargs)

        # importi progetti totale
        tot_progetti = Progetto.objects.filter(comune=c).aggregate(s=Sum('riepilogo_importi')).values()

        # donazioni per il comune considerato
        tot_donazioni = Donazione.objects.filter(comune=c).aggregate(s=Sum('importo')).values()
        if tot_donazioni:
            context['tot_donazioni']= tot_donazioni
            context['donazioni'] = Donazione.objects.filter(comune=c)

        # importi dei progetti per categorie
        context['progetti_categorie'] =  \
            Progetto.objects.filter(comune=c).values('tipologia').\
            annotate(somma_categoria=Sum('riepilogo_importi'))

        # donazioni divise per tipologia cedente
        context['donazioni_categorie'] = \
            Donazione.objects.filter( comune=c).\
            filter(confermato = True).values('tipologia').\
            annotate(somma_categoria = Sum('importo'))

        #iban comune
        iban = Comune.objects.get(pk = c.pk).iban
        if iban:
            context['iban'] = iban

        #lista progetti per questo comune in ordine di costo decrescente
        projects = Progetto.objects.filter(comune = c).order_by('-riepilogo_importi')[:10]

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
        donazioni =  Donazione.objects.all().filter(confermato = True)
        if donazioni:
            context['donazioni'] = donazioni

        #donazioni per categoria
        context['donazioni_categorie'] =\
            Donazione.objects.all().\
            filter(confermato = True).values('tipologia').\
            annotate(somma_categoria = Sum('importo'))


        return context