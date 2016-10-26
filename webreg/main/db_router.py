class LogRouter(object):
    """
    A router to control all database operations on models in the
    auth application.
    """
    def db_for_read(self, model, **hints):
        """
        Attempts to read auth models go to auth_db.
        """
        if model.__name__ == 'LogModel':
            return 'log_db'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write auth models go to auth_db.
        """
        if model.__name__ == 'LogModel':
            return 'log_db'
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if model_name == 'LogModel':
            return db == 'log_db'
        return None