from django.shortcuts import render

from django.views.generic.base import TemplateView


class ReportView(TemplateView):
    
    template_name = "appartments/cabinet_report_per_appartment.html"
