from .common import *
DEBUG = True

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

LOGGING_CONF = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s'
        },
        'simple': {
            'format': '%(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'default'
        },
        'dbhandler': {
            'level': 'DEBUG',
            'class': 'loghandle.loghandle.LogHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'webreg': {
            'handlers': ['dbhandler', 'console'],
            'propagate': False,
            'level': 'DEBUG',
        },
        'cachequery': {
            'handlers': ['dbhandler', 'console'],
            'propagate': False,
            'level': 'DEBUG',
        },
        'qmsfunctions': {
            'handlers': ['dbhandler', 'console'],
            'propagate': False,
            'level': 'DEBUG',
        },
        'command_manage': {
            'handlers': ['dbhandler', 'console'],
            'propagate': False,
            'level': 'DEBUG',
        },
        'default': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    }
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
    }
}


