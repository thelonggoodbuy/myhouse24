from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib import messages

from django.views.generic.base import TemplateView
from django.views.generic.edit import DeleteView, FormView, UpdateView, CreateView
from django.http import HttpResponseRedirect


from .models import UnitOfMeasure, UtilityService
from .forms import HouseEditeFormSet, UtilityServiceEditeFormSet


class UtilityAndMeasuresUnitsEditeList(CreateView):

    model = UtilityService
    fields = '__all__'
    template_name = 'utility_services/utility_and_measure_units_edite_list.html'
    success_url = reverse_lazy('utility_services:report_view')
    measures_units = UnitOfMeasure.objects.all()
    utility_services = UtilityService.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['measures_units_formset'] = HouseEditeFormSet(queryset=self.measures_units, prefix="measures_units")
        context['services_formset'] = UtilityServiceEditeFormSet(queryset=self.utility_services, prefix="services")
        return context

    def post(self, request, *args, **kwargs):
        measures_units_formset = HouseEditeFormSet(request.POST, queryset=self.measures_units, prefix="measures_units")
        services_formset = UtilityServiceEditeFormSet(request.POST, queryset=self.utility_services, prefix="services")
        if measures_units_formset.is_valid() and services_formset.is_valid():
            return self.form_valid(measures_units_formset, services_formset)
        else:
            forms_list = [measures_units_formset, services_formset]
            # print(measures_units_formset.errors)
            # print(services_formset.errors)
            return self.form_invalid(measures_units_formset, services_formset)


    def form_valid(self, measures_units_formset, services_formset):
        measures_units_formset.save()
        services_formset.save()
        success_url = self.success_url
        messages.success(self.request, f"Данные услугах и единицах измерения обновлены.")
        return HttpResponseRedirect(success_url)

    def form_invalid(self, measures_units_formset, services_formset):
        if measures_units_formset.errors:
            for unit_form in measures_units_formset:
                for field, error in unit_form.errors.items():
                    error_text = f"{''.join(error)}"
                    print(f'{field}: {error}')
                    messages.error(self.request, error_text)

        if services_formset.errors:
            for service_form in services_formset:
                for field, error in service_form.errors.items():
                    error_text = f"{''.join(error)}"
                    print(f'{field}: {error}')
                    messages.error(self.request, error_text)
        success_url = self.success_url
        return HttpResponseRedirect(success_url)