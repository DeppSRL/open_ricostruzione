from django_select2 import AutoModelSelect2Field
from open_ricostruzione.models import InterventoProgramma


class InterventoProgrammaChoices(AutoModelSelect2Field):
    queryset = InterventoProgramma.objects.filter().order_by('denominazione')

    search_fields = ['denominazione__icontains', ]

    def label_from_instance(self, obj):
        return obj.denominazione
