"""
WSGI config for open_ricostruzione project.

This module contains the WSGI application used by Django's development server
and any production WSGI deployments. It should expose a module-level variable
named ``application``. Django's ``runserver`` and ``runfcgi`` commands discover
this application via the ``WSGI_APPLICATION`` setting.

Usually you will have the standard Django WSGI application here, but it also
might make sense to replace the whole Django WSGI application with a custom one
that later delegates to the Django one. For example, you could introduce WSGI
middleware here, or combine a Django application with an application of another
framework.

"""
import os
import environ
root = environ.Path(__file__) - 2  # (/open_ricostruzione/project - 2 = /)
env = environ.Env(
    DEBUG=(bool, True),
)
env.read_env(root('config/.env'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", env('DJANGO_SETTINGS_MODULE'))

# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Apply WSGI middleware here.
# from helloworld.wsgi import HelloWorldApplication
# application = HelloWorldApplication(application)
