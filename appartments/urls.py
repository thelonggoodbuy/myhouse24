from django.urls import path

from .views import ReportView


app_name='appartments'

urlpatterns = [
    path('report_view/', ReportView.as_view(), name='report_view'),
]