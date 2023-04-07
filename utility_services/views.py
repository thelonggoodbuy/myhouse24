from django import forms
from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib import messages
from datetime import datetime

from django.views.generic.base import TemplateView
from django.views.generic.edit import DeleteView, FormView, UpdateView, CreateView
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect, JsonResponse


from .models import UnitOfMeasure, UtilityService, Tariff, TariffCell
from .forms import HouseEditeFormSet, UtilityServiceEditeFormSet, TariffMainForm, TariffCellFormSet, CreateTariffCellFormSet, TariffCellForm

# --------------------------------------------------------------------------------------
# ---------------------Utilities-and-measures-logic-------------------------------------
# --------------------------------------------------------------------------------------
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
    

# --------------------------------------------------------------------------------------
# ---------------------Tariff-logic-----------------------------------------------------
# --------------------------------------------------------------------------------------

class TariffListView(TemplateView):
    template_name = "utility_services/tariff_list.html"

    def get(self, request, *args, **kwargs):
        if self.request.is_ajax() and self.request.method == 'GET' and request.GET.get('draw'):
            Q_list = []

            raw_data = Tariff.objects.filter(*Q_list)\
                                .only('title', 'description', 'updated_datetime', 'id')\
                                .order_by()\
                                .values('title', 'description', 'updated_datetime', 'id')
            data = list(raw_data)

            
            for tariff in data:
                if tariff['updated_datetime']:
                    formated_datetime = tariff['updated_datetime'].strftime("%d.%m.%Y - %H:%M")
                    tariff['updated_datetime'] = formated_datetime
                
            
            tariff_get_request = request.GET            
            draw = int(tariff_get_request.get("draw"))
            start = int(tariff_get_request.get("start"))
            length = int(tariff_get_request.get("length"))

            paginator = Paginator(data, length)
            page_number = start / length + 1
            try:
                obj = paginator.page(page_number).object_list
            except PageNotAnInteger:
                obj = paginator(1).object_list
            except EmptyPage:
                obj = paginator.page(1).object_list

            total = len(data)
            records_filter = total

            response = {
                'data': obj,
                'draw': draw,
                'recordsTotal:': total,
                'recordsFiltered': records_filter,
            }
            return JsonResponse(response, safe=False)

        else:
            context = self.get_context_data(**kwargs)
            return self.render_to_response(context)
        

class TariffEditeView(UpdateView):
    form_class = TariffMainForm
    model = Tariff
    template_name = 'utility_services/tariff_edite.html'
    success_url = reverse_lazy('utility_services:tariff_list')
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        utility_services = TariffCell.objects.filter(tariff=self.get_object())
        context['tariff_cell_formset'] = TariffCellFormSet(queryset=utility_services, prefix="tariff_cell")
        return context
    
    def get(self, request, *args, **kwargs):
        if self.request.is_ajax() and self.request.method == 'GET' and self.request.GET.get('choosen_utility_service') != None:
            service_id = self.request.GET['choosen_utility_service']
            service = UtilityService.objects.get(id=service_id)
            unit_measure = service.unit_of_measure.title
            response = {'unit_measure': unit_measure}
            return JsonResponse(response, safe=False)
        else:
            self.object = self.get_object()
            return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **Kwargs):
        tariff_form = TariffMainForm(request.POST, instance=self.get_object())
        tariff_cell_formset = TariffCellFormSet(request.POST, queryset=TariffCell.objects.filter(tariff=self.get_object()), prefix="tariff_cell")
        if tariff_form.is_valid() and tariff_cell_formset.is_valid():
            return self.form_valid(tariff_form, tariff_cell_formset)
        else:
            if tariff_cell_formset.errors:
                for tariff_cell in tariff_cell_formset:
                    for field, error in tariff_cell.errors.items():
                        print(f'{field}: {error}')

        
    def form_valid(self, tariff_form, tariff_cell_formset):
        
        tariff = tariff_form.save(commit=False)
        for tariff_cell in tariff_cell_formset:
            cell = tariff_cell.save(commit=False)
            cell.tariff_id = tariff.id
            cell.save()

        tariff_cell_formset.save()
        tariff.updated_datetime = datetime.now()
        tariff.save()
        success_url = self.success_url
        messages.success(self.request, f"Данные о тарифе {tariff_form.instance.title} обновлены.")
        return HttpResponseRedirect(success_url)


class TariffCreateView(CreateView):
    template_name = 'utility_services/tariff_edite.html'
    form_class = TariffMainForm
    model = Tariff
    success_url = reverse_lazy('utility_services:tariff_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tariff_cell_formset'] = CreateTariffCellFormSet(prefix="tariff_cell")
        return context

    def get(self, request, *args, **kwargs):
        if self.request.is_ajax() and self.request.method == 'GET' and self.request.GET.get('choosen_utility_service') != None:
            service_id = self.request.GET['choosen_utility_service']
            service = UtilityService.objects.get(id=service_id)
            unit_measure = service.unit_of_measure.title
            response = {'unit_measure': unit_measure}
            return JsonResponse(response, safe=False)
        else:
            return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **Kwargs):
        tariff_form = TariffMainForm(request.POST)
        tariff_cell_formset = CreateTariffCellFormSet(request.POST, prefix="tariff_cell")
        if tariff_form.is_valid() and tariff_cell_formset.is_valid():
            return self.form_valid(tariff_form, tariff_cell_formset)
        else:
            if tariff_cell_formset.errors:
                for tariff_cell in tariff_cell_formset:
                    for field, error in tariff_cell.errors.items():
                        print(f'{field}: {error}')

        
    def form_valid(self, tariff_form, tariff_cell_formset):
        tariff = tariff_form.save(commit=False)
        tariff.save()
        for tariff_cell in tariff_cell_formset:
            cell = tariff_cell.save(commit=False)
            cell.tariff = tariff
            cell.save()
        tariff.updated_datetime = datetime.now()
        tariff.save()
        success_url = self.success_url
        messages.success(self.request, f"Создан тариф {tariff_form.instance.title}.")
        return HttpResponseRedirect(success_url)
    

class TariffDeleteView(DeleteView):

    model =  Tariff
    success_url = reverse_lazy('utility_services:tariff_list')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        tariff_title = self.object.title
        success_url = self.get_success_url()
        self.object.delete()
        messages.success(request, (f'Тариф {tariff_title}. Удален.'))
        return HttpResponseRedirect(success_url)
    
class TariffCopyView(TariffCreateView):


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tariff_instance = self.get_object()
        tariff_cell_queryset = TariffCell.objects.filter(tariff=tariff_instance)
        tariff_instance.pk = None

        initial_list_of_dictionary = []
        for tariff_cell in tariff_cell_queryset:
            
            init_dict = {}
            init_dict['utility_service'] = tariff_cell.utility_service
            init_dict['cost_per_unit'] = tariff_cell.cost_per_unit
            init_dict['curency'] = tariff_cell.curency
            initial_list_of_dictionary.append(init_dict)
            
        tariff_instance.pk = None
        context['form'] = TariffMainForm(instance = tariff_instance)
        CopyTariffCellFormSet = forms.inlineformset_factory(Tariff, TariffCell,
                                                        form=TariffCellForm, 
                                                        can_delete=True, 
                                                        extra=len(initial_list_of_dictionary), 
                                                        )
        context['tariff_cell_formset'] = CopyTariffCellFormSet(initial = initial_list_of_dictionary, prefix="tariff_cell")
        return context