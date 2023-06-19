from django.apps import AppConfig


class GeneralStatisticsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'general_statistics'

#     def ready(self):
#         import general_statistics.signals