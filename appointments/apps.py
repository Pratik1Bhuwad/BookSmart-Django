# appointments/apps.py
from django.apps import AppConfig

class AppointmentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'appointments'

    def ready(self):
        # This is a critical step: import the signals file to register the receivers
        import appointments.signals
