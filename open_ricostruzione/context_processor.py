from django.conf import settings
from territori.models import Territorio

def main_settings(request):
    return {
        "DEBUG": settings.DEBUG,
        "TEMPLATE_DEBUG": settings.TEMPLATE_DEBUG,
        "territori_cratere": list(Territorio.objects.filter(istat_id__in=settings.COMUNI_CRATERE).order_by('prov')),
        "url": request.build_absolute_uri(),
        }