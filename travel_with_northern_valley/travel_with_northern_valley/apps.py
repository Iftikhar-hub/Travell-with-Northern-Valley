# travel_with_northern_valley/apps.py

from django.apps import AppConfig

class TravelWithNorthernValleyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'travel_with_northern_valley'

    def ready(self):
        import travel_with_northern_valley.signals  # ⚠ This is what triggers signal loading
