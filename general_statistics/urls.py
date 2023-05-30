from .views import GeneralStatisticsView
from django.urls import path

app_name='general_statistics'




urlpatterns = [

        path('admin_general_statistics/', GeneralStatisticsView.as_view(), name='admin_general_statistics'),

               ]