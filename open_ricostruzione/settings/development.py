# -*-coding: UTF-8 -*-
from base import *

# root = environ.Path(__file__) - 2  # (/open_ricostruzione/open_ricostruzione/settings/ - 4 = /)
#
# # set default values and casting
# env = environ.Env(
#     DEBUG=(bool, True),
# )
# env.read_env(root('.env'))

########## DEBUG CONFIGURATION
DEBUG = env.bool('DEBUG', True)
TEMPLATE_DEBUG = env.bool('TEMPLATE_DEBUG', True)
########## END DEBUG CONFIGURATION

########## TOOLBAR CONFIGURATION
# See: https://github.com/django-debug-toolbar/django-debug-toolbar#installation
INSTALLED_APPS += (
    'debug_toolbar',
)

# See: https://github.com/django-debug-toolbar/django-debug-toolbar#installation
INTERNAL_IPS = ('127.0.0.1',)

# See: https://github.com/django-debug-toolbar/django-debug-toolbar#installation
MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

# See: https://github.com/django-debug-toolbar/django-debug-toolbar#installation
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
    'SHOW_TEMPLATE_CONTEXT': True,
}
########## END TOOLBAR CONFIGURATION

LOG_PATH = os.path.join(PROJECT_PATH,'open_ricostruzione', 'log')

LOGGING['handlers']['file']['filename'] = "{}/logfile".format(LOG_PATH)
LOGGING['handlers']['management_logfile']['filename'] = "{}/mnglogfile".format(LOG_PATH)

MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media')
MEDIA_URL = '/media/'
SOCIABLE_IMAGE_PATH ="sociable"

STATIC_ROOT = os.path.join(PROJECT_PATH, 'sitestatic')
STATIC_URL = '/static/'


########## SECRET CONFIGURATION
SECRET_KEY = env('SECRET_KEY')  # Raises ImproperlyConfigured exception if SECRET_KEY not in os.environ
########## END SECRET CONFIGURATION
