import logging.config
from django.apps import AppConfig
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s'
        },
        'webreg': {
            'format': '%(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'default'
        },
        'webreg': {
            'level': 'DEBUG',
            'class': 'main.loghandle.LogHandler',
            'formatter': 'webreg'
        },
    },
    'loggers': {
        'webreg': {
            'handlers': ['console', 'webreg'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'default': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    }
}


class MainAppConfig(AppConfig):
    name = 'main'
    verbose_name = "Main Application"

    def ready(self):
        logging.config.dictConfig(LOGGING)
