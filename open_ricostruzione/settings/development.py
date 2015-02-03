# -*-coding: UTF-8 -*-
from base import *

root = environ.Path(__file__) - 2  # (/open_ricostruzione/open_ricostruzione/settings/ - 4 = /)

# set default values and casting
env = environ.Env(
    DEBUG=(bool, True),
)
env.read_env(root('.env'))

########## DEBUG CONFIGURATION
DEBUG = env.bool('DEBUG', False)
TEMPLATE_DEBUG = env.bool('TEMPLATE_DEBUG', False)
########## END DEBUG CONFIGURATION

DEVELOPMENT=True

DATABASES = {
    'default': env.db('DB_DEFAULT_URL'),
}


MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')
MEDIA_URL = '/media/'
SOCIABLE_IMAGE_PATH ="sociable"

STATIC_ROOT = os.path.join(PROJECT_ROOT, 'sitestatic')
STATIC_URL = '/static/'


########## SECRET CONFIGURATION
SECRET_KEY = env('SECRET_KEY')  # Raises ImproperlyConfigured exception if SECRET_KEY not in os.environ
########## END SECRET CONFIGURATION
