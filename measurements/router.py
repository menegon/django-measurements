from measurements.settings import DATABASE_ROUNTING

class MeasurementsRouter:
    """
    A router to control all database operations on models in the
    measurements application.
    """
    def db_for_read(self, model, **hints):
        """
        Attempts to read measurements models go to measurements_db.
        """
        if model._meta.app_label == 'measurements':
            return DATABASE_ROUNTING
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write measurements models go to measurements_db.
        """
        if model._meta.app_label == 'measurements':
            return DATABASE_ROUNTING
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the measurements app is involved.
        """
        if obj1._meta.app_label == 'measurements' or \
           obj2._meta.app_label == 'measurements':
           return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the measurements app only appears in the 'measurements_db'
        database.
        """
        if app_label == 'measurements':
            return db == DATABASE_ROUNTING
        return None