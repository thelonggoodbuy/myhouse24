from django.urls import path

from .views import CRMReportView, ReceiptListView, AddReceiptView,\
    ReceiptCardView, ReceiptTemplateListView, ReceiptTemplateEditeView


app_name='receipts'

urlpatterns = [
    path('crm_report_view/', CRMReportView.as_view(), name='crm_report_view'),

    path('receipt_list/', ReceiptListView.as_view(), name='receipt_list'),
    path('add_receipt_view/', AddReceiptView.as_view(), name='add_receipt'),
    path('receipt_detail/', ReceiptCardView.as_view(), name='receipt_detail'),
    path('receipt_detail/<int:pk>', ReceiptCardView.as_view(), name='receipt_detail'),
    path('receipt_list_of_templates', ReceiptTemplateListView.as_view(), name='receipt_template_list_view'),
    path('receipt_list_of_templates/<int:pk>', ReceiptTemplateListView.as_view(), name='receipt_template_list_view'),
    path('receipt_template_edite_view/',ReceiptTemplateEditeView.as_view(), name='receipt_template_edite_view'),
    # path('return_xlm_file/<int:receipt_id>/', return_xlm_file, name='return_xlm_file'), 
    # path('return_xlm_file/<int:receipt_id>', return_xlm_file, name='return_xlm_file'), 
    # path('return_xlm_file/<int:receipt_id>/<int:template_id>', return_xlm_file, name='return_xlm_file'), 
    
]