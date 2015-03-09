from django.conf import settings
from territori.models import Territorio

def main_settings(request):
    return {
        "DEBUG": settings.DEBUG,
        "TEMPLATE_DEBUG": settings.TEMPLATE_DEBUG,
        "territori_cratere": list(Territorio.get_territori_cratere()),
        "url": request.build_absolute_uri(),
        }