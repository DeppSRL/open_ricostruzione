from django.conf import settings
from django.contrib.sites.models import get_current_site
from .models import TipoImmobile, SoggettoAttuatore, UltimoAggiornamento


from .forms import InterventoProgrammaSearchFormNavbar, ImpresaSearchFormNavbar
from territori.models import Territorio


def main_settings(request):
    return {
        'site': get_current_site(request),
        "DEBUG": settings.DEBUG,
        "TEMPLATE_DEBUG": settings.TEMPLATE_DEBUG,
        "INSTANCE_TYPE": settings.INSTANCE_TYPE,
        "territori_cratere": list(Territorio.get_territori_cratere()),
        "tipologie_immobile": TipoImmobile.get_tipologie(),
        "tipologie_sogg_att": SoggettoAttuatore.get_tipologie(),
        "interventi_search_form": InterventoProgrammaSearchFormNavbar(),
        "impresa_search_form": ImpresaSearchFormNavbar(),
        "url": request.build_absolute_uri(),
        "ultimo_aggiornamento": UltimoAggiornamento.objects.get(tipologia=UltimoAggiornamento.TIPOLOGIA.INTERVENTI,).data,
        "n_comuni_cratere": len(settings.COMUNI_CRATERE),
        "n_comuni_monitorati": Territorio.objects.filter(interventoprogramma__isnull=False, istat_id__in=settings.COMUNI_CRATERE).distinct('slug').count()
        }
