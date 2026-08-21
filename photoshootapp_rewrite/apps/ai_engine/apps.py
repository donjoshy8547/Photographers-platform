from django.apps import AppConfig


class AIEngineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ai_engine'
    verbose_name = 'AI Engine'

    def ready(self):
        # Initialize AI services and signal handlers
        try:
            from . import tasks
            # tasks.setup_signal_handlers()  # Uncomment when signals are ready
        except ImportError:
            pass
