from django_select2 import AutoModelSelect2Field

from .models import InterventoProgramma, Impresa


class InterventoProgrammaChoices(AutoModelSelect2Field):
    queryset = InterventoProgramma.objects.filter().order_by('denominazione')

    search_fields = ['denominazione__icontains', ]

    def label_from_instance(self, obj):
        return obj.denominazione


class ImpresaChoices(AutoModelSelect2Field):
    queryset = Impresa.objects.filter().order_by('ragione_sociale')

    search_fields = ['ragione_sociale__icontains', ]

    def label_from_instance(self, obj):
        return obj.ragione_sociale
