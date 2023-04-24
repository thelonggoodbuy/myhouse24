from django.urls import path

from .views import CRMReportView, ReceiptListView, AddReceiptView


app_name='receipts'

urlpatterns = [
    path('crm_report_view/', CRMReportView.as_view(), name='crm_report_view'),

    path('receipt_list/', ReceiptListView.as_view(), name='receipt_list'),
    path('add_receipt_view/', AddReceiptView.as_view(), name='add_receipt'),
]