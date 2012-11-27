from django.conf import settings
from open_ricostruzione.models import *
from django.db.models import Count


def main_settings(request):
    territori=[]

    territori = Territorio.objects.filter(tipo_territorio = "C").\
                    annotate(c = Count("progetto")).filter(c__gt=0).order_by("-cod_provincia")
#    for p in Territorio.objects.filter(tipo_territorio="P").order_by("denominazione"):
#
#        active_comuni=[]
#        for c in p.get_comuni_with_progetti():
#
#            active_comuni.append({
#                'nome':c.denominazione,
#                'slug':c.slug,
#            })
#
#        territori.append({
#            'nome': p.denominazione,
#            'comuni': active_comuni,
#            })
#

    return {
        "DEBUG": settings.DEBUG,
        "tipologie_progetti": TipologiaProgetto.objects.all().values("denominazione").order_by("denominazione"),
        "territori": territori,
        }