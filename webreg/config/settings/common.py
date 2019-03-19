import os
import json

from unipath import Path
from django.core.exceptions import ImproperlyConfigured

DEBUG = False

ROOT_POJECT_DIR = Path(__file__).ancestor(4)

BASE_DIR = Path(__file__).ancestor(3)
CONFIG_DIR = Path(__file__).ancestor(2)

MEDIA_ROOT = ROOT_POJECT_DIR.child("media")
STATIC_ROOT = ROOT_POJECT_DIR.child("static")

LOG_DIRECTORY = ROOT_POJECT_DIR.child('log')

STATICFILES_DIRS = (
)
TEMPLATE_DIRS = ()

PROJECT_NAME = BASE_DIR.split(os.sep)[-1]

with open(Path(CONFIG_DIR, "secrets.json")) as f:
    secrets = json.loads(f.read())


def get_secret(setting, secrets=secrets):
    """Get the secret variable or return explicit exception."""
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {0} environment variable".format(setting)
        raise ImproperlyConfigured(error_msg)

SECRET_KEY = get_secret("SECRET_KEY")


# Application definition


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'django.contrib.sites',
    'constance.backends.database',
    'constance',
    'crispy_forms',
    'flatblocks',
    'djcelery',
    'djcelery_email',
    'registration',
    'compressor'
]


LOCAL_APPS = (
    'util',
    'loghandle',
    'catalogs',
    'main',
    'patient_writer',
    'patient_writer.accounts',
    'qmsmodule',
    'qmsintegration',
    'mixins',
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'main.middleware.AddUserProfileMiddleware',
    'main.middleware.GlobalRequestMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR.child("templates"), ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'main.context_processors.patient'
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'main.authentication.PolisNumberBackend'
]

ACCOUNT_ACTIVATION_DAYS = 2

# имя настроек профиля по умолчанию
DEFAULT_PROFILE_SETTINGS_NAME = "default"


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Asia/Krasnoyarsk'

USE_I18N = True

USE_L10N = True

DATE_INPUT_FORMATS = '%d.%m.%Y'

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'
ADMIN_MEDIA_PREFIX = STATIC_URL
MEDIA_URL = '/media/'

for item in LOCAL_APPS:
    INSTALLED_APPS += (item, )
    # STATICFILES_DIRS += ((item, Path(BASE_DIR, item, 'static')), )

DATABASE_ROUTERS = ['loghandle.db_router.LogRouter']

CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'

CONSTANCE_CONFIG = {
    'QMS_INTEGRATION_ENABLE': (True, 'QMS integration enable')
}


CRISPY_TEMPLATE_PACK = 'bootstrap3'

AUTH_USER_EMAIL_UNIQUE = True

EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'
EMAIL_HOST = get_secret("EMAIL_HOST")
EMAIL_PORT = 25
EMAIL_HOST_USER = get_secret("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = get_secret("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'no-reply@skc-fmba.ru'

SMS_URL = get_secret("SMS_URL")

from celery import Celery
celery = Celery(
    'webreg',
    broker='redis://127.0.0.1:6379/15',
    backend='redis',
    include=['main.tasks', 'djcelery_email.tasks']
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

COMPRESS_CSS_FILTERS = [
    'compressor.filters.cssmin.CSSMinFilter'
]
COMPRESS_JS_FILTERS = [
    'compressor.filters.jsmin.JSMinFilter'
]

from patient_writer.settings import *
