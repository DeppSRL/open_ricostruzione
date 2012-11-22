from django.views.generic import TemplateView, DetailView
from open_ricostruzione.models import *

class HomeView(TemplateView):
    template_name = "home.html"

class ProgettoView(DetailView):
    model = Progetto
    context_object_name = "progetto"
    template_name = 'progetto.html'

    def get_context_data(self, **kwargs ):

        self.context = super(ProgettoView, self).get_context_data(**kwargs)
        return self.context

class ComuneView(DetailView):
    model = Comune
    context_object_name = "comune"
    template_name = 'comune.html'

    def get_context_data(self, **kwargs ):

        self.context = super(ComuneView, self).get_context_data(**kwargs)
        return self.context
