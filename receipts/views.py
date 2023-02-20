from django.shortcuts import render

from django.views.generic.base import TemplateView


class CRMReportView(TemplateView):
    
    template_name = "receipts/crm_report.html"
