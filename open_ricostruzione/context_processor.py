from django.conf import settings

def main_settings(request):
    return {
        "DEBUG": settings.DEBUG,
        }