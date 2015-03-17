from django.conf import settings
from territori.models import Territorio
from open_ricostruzione.models import TipoImmobile, SoggettoAttuatore


def main_settings(request):
    return {
        "DEBUG": settings.DEBUG,
        "TEMPLATE_DEBUG": settings.TEMPLATE_DEBUG,
        "territori_cratere": Territorio.get_territori_cratere(),
        "tipologie_immobile": TipoImmobile.get_tipologie(),
        "tipologie_sogg_att": SoggettoAttuatore.get_tipologie(),
        "url": request.build_absolute_uri(),
        }