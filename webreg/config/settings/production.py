from .base import *

DEBUG = False

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',  # 'django.db.backends.sqlite3',
        'NAME': PROJECT_NAME,
        'USER': PROJECT_NAME + '_user',
        'PASSWORD': get_secret("DB_PASSWORD"),
        'HOST': '',
        'PORT': ''
    }
}

