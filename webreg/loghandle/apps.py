import logging.config
from django.apps import AppConfig

from django.conf import settings


class LoghandleAppConfig(AppConfig):
    name = 'loghandle'
    verbose_name = "Application for manage logs"

    def ready(self):
        logging.config.dictConfig(settings.LOGGING_CONF)
