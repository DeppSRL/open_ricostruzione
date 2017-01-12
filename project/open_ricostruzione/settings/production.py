# -*-coding: UTF-8 -*-
"""Production settings and globals."""
import environ
from base import *

root = environ.Path(__file__) - 2  # (/open_ricostruzione/open_ricostruzione/settings/ - 4 = /)

# set default values and casting
env = environ.Env(
    DEBUG=(bool, True),
)

env.read_env(root('config/.env'))

########## DEBUG CONFIGURATION
DEBUG = env.bool('DEBUG', False)
TEMPLATE_DEBUG = env.bool('TEMPLATE_DEBUG', False)
########## END DEBUG CONFIGURATION

POSTGIS_VERSION=( 2, 1 )
DATABASES = {
    'default': env.db('DB_DEFAULT_URL'),
}

MEDIA_ROOT = os.path.join(REPO_PATH, 'public', 'media')
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(REPO_PATH, 'public', 'static')
STATIC_URL = '/static/'

########## SECRET CONFIGURATION
SECRET_KEY = env('SECRET_KEY')  # Raises ImproperlyConfigured exception if SECRET_KEY not in os.environ
########## END SECRET CONFIGURATION
