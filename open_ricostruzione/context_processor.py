from django.conf import settings
from open_ricostruzione.forms import InterventoProgrammaSearchFormNavbar, ImpresaSearchFormNavbar
from territori.models import Territorio
from open_ricostruzione.models import TipoImmobile, SoggettoAttuatore


def main_settings(request):
    return {
        "DEBUG": settings.DEBUG,
        "TEMPLATE_DEBUG": settings.TEMPLATE_DEBUG,
        "INSTANCE_TYPE": settings.INSTANCE_TYPE,
        "territori_cratere": Territorio.get_territori_cratere(),
        "tipologie_immobile": TipoImmobile.get_tipologie(),
        "tipologie_sogg_att": SoggettoAttuatore.get_tipologie(),
        "interventi_search_form": InterventoProgrammaSearchFormNavbar(),
        "impresa_search_form": ImpresaSearchFormNavbar(),
        "url": request.build_absolute_uri(),
        }