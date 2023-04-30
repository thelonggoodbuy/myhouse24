from django.urls import path

from .views import CRMReportView, ReceiptListView, AddReceiptView, ReceiptCardView


app_name='receipts'

urlpatterns = [
    path('crm_report_view/', CRMReportView.as_view(), name='crm_report_view'),

    path('receipt_list/', ReceiptListView.as_view(), name='receipt_list'),
    path('add_receipt_view/', AddReceiptView.as_view(), name='add_receipt'),
    path('receipt_detail/', ReceiptCardView.as_view(), name='receipt_detail'),
    path('receipt_detail/<int:pk>', ReceiptCardView.as_view(), name='receipt_detail'),
]