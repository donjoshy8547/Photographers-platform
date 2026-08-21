from django.apps import AppConfig


class MediaLibraryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.media_library'
    verbose_name = 'Media Library'

    def ready(self):
        # Import signal handlers
        try:
            from . import signals
        except ImportError:
            pass