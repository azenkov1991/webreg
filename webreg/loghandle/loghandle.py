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

        log_directory_for_logger = settings.LOG_DIRECTORY + os.sep + record.name + os.sep + record.levelname

        if not os.path.exists(log_directory_for_logger):
            os.makedirs(log_directory_for_logger)

        file_name = log_directory_for_logger + os.sep + date.today().strftime("%Y%m%d") + ".log"

        with open(file_name, 'a') as f:
            f.write(datetime.now().strftime("%H:%M") + " | " + str(session_key) + " | " + record.getMessage() + "\n")



