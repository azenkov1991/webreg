import os
from logging import Handler
from datetime import date, datetime
from django.conf import settings
from .models import LogModel
from main.middleware import GlobalRequestMiddleware


class LogHandler(Handler):
    def emit(self, record):
        session = GlobalRequestMiddleware.get_current_session()
        if session:
            session_key = session.session_key
        else:
            session_key = None
        log = LogModel(
            level=record.levelname,
            logger_name=record.name,
            source_file=record.pathname,
            message=record.getMessage(),
            session_key=session_key
        )

        log.save()


class FileLogHandler(Handler):
    def emit(self, record):
        session = GlobalRequestMiddleware.get_current_session()
        if session:
            session_key = session.session_key
        else:
            session_key = 'no_session_key'

        if not os.path.exists(settings.LOG_DIRECTORY):
            os.makedirs(settings.LOG_DIRECTORY)

        file_name = settings.LOG_DIRECTORY + os.sep + self.name + "-" + date.today().strftime("%Y%m%d")
        with open(file_name, 'a') as f:
            f.write(datetime.now().strftime("%H:%M") + " | " + session_key + " | " + record.getMessage() + "\n")



