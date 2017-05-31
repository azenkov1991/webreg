from .default import *
DEBUG = True

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases



GOOD_CACHE_SETTINGS = {
            'CONNECTION_PARAM': {
                   'user': '_system',
                   'password': 'SYS',
                   'host': '10.1.2.105',
                   'port': '1972',
                   'wsdl_port': '57772',
                   'namespace': 'SKCQMS'
            },
            'CACHE_CODING': 'cp1251',
            'DATABASE_CODE': u'СКЦ'
        }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',  # 'django.db.backends.sqlite3',
        'NAME': PROJECT_NAME,
        'USER': PROJECT_NAME + '_user',
        'PASSWORD': get_secret("DB_PASSWORD"),
        'HOST': '127.0.0.1',
        'PORT': '5432'
    },
    'log_db': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': PROJECT_NAME + 'log',
        'USER': PROJECT_NAME + '_user',
        'PASSWORD': get_secret("DB_LOG_PASSWORD"),
        'HOST': '127.0.0.1',
        'PORT': '5432'
    },
    'old_db': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': get_secret('OLDDB_NAME'),
        'USER': get_secret('OLDDB_USER'),
        'PASSWORD': get_secret('OLDDB_PASSWORD'),
        'HOST': get_secret('OLDDB_HOST'),
        'PORT': get_secret('OLDDB_PORT'),
    },
}


