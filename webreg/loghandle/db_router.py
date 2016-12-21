class LogRouter(object):
    """
    A router to control all database operations on models in the
    auth application.
    """
    def db_for_read(slf, model, **hints):
        """
        Attempts to read auth models go to auth_db.
        """
        if model._meta.app_label == 'loghandle':
            return 'log_db'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write auth models go to auth_db.
        """
        if model._meta.app_label == 'loghandle':
            return 'log_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the auth app is involved.
        """
        if obj1._meta.app_label == 'loghandle' or \
           obj2._meta.app_label == 'loghandle':
           return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'loghandle':
            return db == 'log_db'
        return None
