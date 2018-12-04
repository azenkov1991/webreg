from logging import Handler
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
