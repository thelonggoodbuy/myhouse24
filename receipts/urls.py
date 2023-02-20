from django.urls import path

from .views import CRMReportView


app_name='receipts'

urlpatterns = [
    path('crm_report_view/', CRMReportView.as_view(), name='crm_report_view'),
]