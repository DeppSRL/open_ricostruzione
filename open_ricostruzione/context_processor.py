from django.conf import settings
from open_ricostruzione.models import *
from django.db.models import Count


def main_settings(request):
    territori=[]

#prende la lista di tutti i comuni con almeno un progetto ordinati per provincia
    territori = Territorio.objects.filter(tipo_territorio = "C").\
                    annotate(c = Count("progetto")).filter(c__gt=0).order_by("-cod_provincia")

    return {
        "DEBUG": settings.DEBUG,
        "tipologie_progetti": TipologiaProgetto.objects.all().values("denominazione").order_by("denominazione"),
        "territori": territori,
        }