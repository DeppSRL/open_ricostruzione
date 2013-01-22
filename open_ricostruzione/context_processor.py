from django.conf import settings
from open_ricostruzione.models import *
from django.db.models import Count


def main_settings(request):
    territori=[]

#prende la lista di tutti i comuni con almeno un progetto ordinati per provincia
    territori = Territorio.objects.filter(tipo_territorio = "C",cod_comune__in=settings.COMUNI_CRATERE).\
                    annotate(c = Count("progetto")).filter(c__gt=0).order_by("-cod_provincia")

    territori_alfabetico = Territorio.objects.filter(tipo_territorio = "C",cod_comune__in=settings.COMUNI_CRATERE).\
        annotate(c = Count("progetto")).filter(c__gt=0).order_by("denominazione")

    return {
        "DEBUG": settings.DEBUG,
        "TEMPLATE_DEBUG": settings.TEMPLATE_DEBUG,
        "tipologie_progetti": TipologiaProgetto.objects.\
            filter(progetto__id_padre__isnull=True).\
            annotate(c=Count('progetto')).values("denominazione","slug","c").\
            filter(c__gt=0).order_by("denominazione"),
        "tipologie_donazioni": TipologiaCedente.objects.\
            exclude(denominazione__iexact="Privati Cittadini").\
            filter(donazione__confermato=True).\
            annotate(c=Count('donazione')).values("denominazione","slug","c").filter(c__gt=0).order_by("denominazione"),
        "territori": territori,
        "territori_alfabetico": territori_alfabetico,
        "tipologia_privati":TipologiaCedente.objects.get(codice='1'),
        }