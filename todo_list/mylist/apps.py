from django.apps import AppConfig


class MylistConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "mylist"
    def ready(self):
        """Initialize database when app is ready."""
        from .database import init_database
        try:
            init_database()
        except Exception:
            pass  # Database might not be available during migrations

