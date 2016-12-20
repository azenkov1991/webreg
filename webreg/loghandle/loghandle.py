from logging import Handler
from .models import LogModel


class LogHandler(Handler):
    def emit(self, record):
        log = LogModel(level=record.levelname,
                       logger_name=record.name,
                       source_file=record.pathname,
                       message=record.getMessage())
        log.save()
