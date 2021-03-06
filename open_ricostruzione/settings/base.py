# Django settings for open_ricostruzione project.
import os
from os.path import abspath, basename, dirname, join, normpath
from sys import path
from environ import Env

######### PATH CONFIGURATION
PACKAGE_PATH = dirname(dirname(abspath(__file__)))
PACKAGE_NAME = basename(PACKAGE_PATH)
PROJECT_PATH = REPO_PATH = dirname(PACKAGE_PATH)

RESOURCE_DIR = 'resources'
RESOURCES_PATH = join(REPO_PATH, RESOURCE_DIR)

LOG_PATH = join(RESOURCES_PATH,'logs')

FIXTURES_DIR = 'fixtures'
FIXTURES_PATH = join(REPO_PATH, FIXTURES_DIR)

# Add our project to our pythonpath, this way we don't need to type our project
# name in our dotted import paths:
path.append(PROJECT_PATH)

# load environment variables
Env.read_env(normpath(join(REPO_PATH, '.env')))
env = Env()
######### END PATH CONFIGURATION

########## OPEN_RICOSTRUZIONE CONFIGURATION
DEBUG = env.bool('DEBUG', False)
TEMPLATE_DEBUG = env.bool('TEMPLATE_DEBUG', False)
INSTANCE_TYPE = env.str('INSTANCE_TYPE', '')

ADMINS = (
    ('Guglielmo Celata', 'guglielmo@depp.it'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': env.db('DB_DEFAULT_URL', default='sqlite:///{0}'.format(normpath(join(RESOURCES_PATH, 'db', 'default.db')))),
}       

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Rome'

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'it-IT'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = normpath(join(RESOURCES_PATH, 'media'))

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = normpath(join(RESOURCES_PATH, 'static'))

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    normpath(join(PACKAGE_PATH, 'static')),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = env.str('SECRET_KEY', None)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',

)

ROOT_URLCONF = 'open_ricostruzione.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = '%s.wsgi.application' % PACKAGE_NAME

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    normpath(join(PACKAGE_PATH, 'templates')),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',

    # bilanci project context processor
    'open_ricostruzione.context_processor.main_settings',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
    'django_extensions',
    'front',
    # 'disqus',
    'rest_framework',
    'django.contrib.gis',
    'open_ricostruzione',
    'open_ricostruzione.depp_humanize',
    'territori',
    'bootstrap_pagination',
    'django_select2',
    'django_filters',
    'robots',

)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 30000,
    }
}

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s.%(msecs).03d] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': normpath(join(LOG_PATH, 'openricostruzione.log')),
            'formatter': 'verbose'
        },
        'management_logfile': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': normpath(join(LOG_PATH, 'management.log')),
            'mode': 'w',
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'openricostruzione': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True
        },  
        'csvimport': {
            'handlers': ['console', 'management_logfile'],
            'level': 'DEBUG',
            'propagate': True,
        }
    }
}

PROVINCE_CRATERE = [u'Bologna', u'Ferrara', u'Modena', u"Reggio nell'Emilia"]

COMUNI_CRATERE = [u'037002', u'037003', u'037005', u'037017', u'037019', u'037024', u'037028', u'037035', u'037038',
                  u'037039', u'037048', u'037050', u'037052', u'037053', u'037055', u'037056', u'037006', u'037009',
                  u'037032', u'037037', u'038003', u'038004', u'038016', u'038018', u'038021', u'038022', u'038008',
                  u'038001', u'036001', u'036002', u'036003', u'036004', u'036005', u'036006', u'036009', u'036010',
                  u'036012', u'036021', u'036022', u'036027', u'036028', u'036034', u'036037', u'036038', u'036039',
                  u'036044', u'036023', u'035005', u'035006', u'035020', u'035021', u'035023', u'035024', u'035026',
                  u'035028', u'035032', u'035034', u'035035', u'035037', u'035009', u'035033']

DISQUS_WEBSITE_SHORTNAME = env('DISQUS_WEBSITE_SHORTNAME')

DISQUS_API_KEY = env('DISQUS_API_KEY')

OR_BLOG_FEED = 'http://blog.openricostruzione.it/?feed=rss2'

OP_API = {
    'base_url': env('OP_API_DOMAIN'),
    'username': env('OP_API_USERNAME'),
    'password': env('OP_API_PASSWORD'),
}

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [],
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination'
}

SOGG_ATTUATORE_MAP_FILE_PATH = env.str('SOGG_ATTUATORE_MAP_FILE_PATH', '')

# valori degli stati degli interventi che indicano lo stato di avanzamento
STATI_PROGETTAZIONE = [u'1', u'2', u'3', u'4', u'5', u'7', ]
STATI_IN_CORSO = [u'6', u'8', u'9', u'12', ]
STATI_CONCLUSI = [u'10', u'11', ]

# tipologia cedente in PRIVATE_TIPOLOGIA_CEDENTE are private citizens'ones so the Denominazione will be obscured
PRIVATE_TIPOLOGIA_CEDENTE = [u'4', ]
LOCALITA_MAP_BOUNDS_WIDTH = 0.02

THEMATIC_MAP_BOUNDS = {
    'sw': {'lat': 43.714294, 'lon': 8.316650},
    'ne': {'lat': 45.743928, 'lon': 13.315430},
}

THEMATIC_MAP_CENTER = {
    'lat': 44.6500,
    'lon': 10.9333
}

N_PROGETTI_FETCH = 4
N_IMPRESE_FETCH = 6
N_SOGG_ATT_FETCH = 5

OPENDATA_ROOT = normpath(join(REPO_PATH, 'scarico_dati'))
OPENDATA_URL = '/scarico_dati/'
