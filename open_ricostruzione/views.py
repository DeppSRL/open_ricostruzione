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
        c = self.object()
        context = super(ComuneView, self).get_context_data(**kwargs)

        return context
