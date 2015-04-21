from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import SimpleListFilter
import django_filters
from open_ricostruzione.models import InterventoProgramma
from territori.models import Territorio

class TerritorioHasObject(SimpleListFilter):
    title = _('Territorio')
    parameter_name = 'territorio_has_object'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        t_list = self.get_interested_territori()
        territori_tuple = ()
        for t in t_list:
            territori_tuple+= ((t['slug'],"{} ({})".format(t['denominazione'],t['prov'])),)
        return territori_tuple

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value():
            return queryset.filter(territorio__slug=self.value())

        return queryset


class TerritorioWithDonazione(TerritorioHasObject):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.

    def get_interested_territori(self):
        return Territorio.objects.filter(donazione__isnull=False, tipologia="C").order_by(
            'denominazione').distinct().values('denominazione','prov','slug')


class TerritorioWithIntervento(TerritorioHasObject):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.

    def get_interested_territori(self):
        return Territorio.objects.filter(interventoprogramma__isnull=False, tipologia="C").order_by(
            'denominazione').distinct().values('denominazione','prov','slug')


class InterventoProgrammaFilter(django_filters.FilterSet):
    class Meta:
        model = InterventoProgramma
        order_by = ['denominazione', 'tipo_immobile__slug', 'territorio']
        fields = {
            'territorio__slug': ['exact'],
            'tipo_immobile__slug': ['exact'],
            'soggetto_attuatore__slug': ['exact'],
            'interventopiano__intervento__imprese__slug': ['exact'],
             }