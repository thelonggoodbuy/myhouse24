from django.urls import path

from .views import CRMReportView, ReceiptListView, AddReceiptView, ReceiptUpdateView,\
    ReceiptCardView, ReceiptTemplateListView, ReceiptTemplateEditeView, ReceiptDeleteView,\
    RequisiteUpdateView


app_name='receipts'

urlpatterns = [
    path('crm_report_view/', CRMReportView.as_view(), name='crm_report_view'),

    path('receipt_list/', ReceiptListView.as_view(), name='receipt_list'),
    path('add_receipt_view/', AddReceiptView.as_view(), name='add_receipt'),
    path('edit_receipt/', ReceiptUpdateView.as_view(), name='edit_receipt'),
    path('edit_receipt/<int:pk>', ReceiptUpdateView.as_view(), name='edit_receipt'),
    path('receipt_detail/', ReceiptCardView.as_view(), name='receipt_detail'),
    path('receipt_detail/<int:pk>', ReceiptCardView.as_view(), name='receipt_detail'),
    path('receipt_delete/', ReceiptDeleteView.as_view(), name='receipt_delete'),
    path('receipt_delete/<int:pk>', ReceiptDeleteView.as_view(), name='receipt_delete'),
    path('receipt_list_of_templates', ReceiptTemplateListView.as_view(), name='receipt_template_list_view'),
    path('receipt_list_of_templates/<int:pk>', ReceiptTemplateListView.as_view(), name='receipt_template_list_view'),
    path('receipt_template_edite_view/',ReceiptTemplateEditeView.as_view(), name='receipt_template_edite_view'),
    path('requiside_update/', RequisiteUpdateView.as_view(), name='requiside_update'),
    path('receipt_delete/<int:pk>', ReceiptDeleteView.as_view(), name='receipt_delete'),
    
]