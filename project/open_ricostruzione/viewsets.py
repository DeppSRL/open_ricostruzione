from django.conf import settings
from django.core.paginator import Paginator
from rest_framework import viewsets

from .models import InterventoProgramma, Donazione
from .serializers import DonazioneSerializer, InterventoProgrammaSerializer


class InterventoProgrammaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InterventoProgramma.objects.all().order_by('-denominazione')
    serializer_class = InterventoProgrammaSerializer
    paginator_class = Paginator
    paginate_by = 100


class DonazioneViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Donazione.objects.all().order_by('-importo')
    serializer_class = DonazioneSerializer
    paginator_class = Paginator
    paginate_by = 100

    def get_queryset(self):
        queryset = self.queryset

        # manipulates queryset to obscure private citizen name in the list
        for donazione in queryset:
            if donazione.tipologia_cedente in settings.PRIVATE_TIPOLOGIA_CEDENTE:
                donazione.denominazione = ""

        return queryset
