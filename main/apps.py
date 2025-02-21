from django.apps import AppConfig

# Configuration class for the main application
class MainConfig(AppConfig):
    # Default primary key field type
    default_auto_field = 'django.db.models.BigAutoField'
    # Name of the application
    name = 'main'