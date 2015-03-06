from django.conf import settings
from open_ricostruzione.models import *


def main_settings(request):
    return {
        "DEBUG": settings.DEBUG,
        "TEMPLATE_DEBUG": settings.TEMPLATE_DEBUG,
        "territori_cratere": settings.COMUNI_CRATERE,
        "url": request.build_absolute_uri(),
        }