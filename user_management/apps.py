from django.apps import AppConfig


class UserManagementConfig(AppConfig):
    """Configuration for the user_management app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user_management'

def ready(self):
        """This ensures the 'Game Keepers' group is created, but only after Django is fully loaded."""
        import django
        if django.apps.apps.ready:  # ✅ Prevents early database access
            from django.contrib.auth.models import Group
            Group.objects.get_or_create(name="Game Keepers")