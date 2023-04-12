from django import forms
from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib import messages
from datetime import datetime
from babel.dates import format_date

from django.views.generic.base import TemplateView
from django.views.generic.edit import DeleteView, FormView, UpdateView, CreateView
from django.views.generic.list import ListView


from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect, JsonResponse
from django.db.models import F, Q, OuterRef, Subquery, CharField, Value, Count, Sum, DecimalField
import locale


from .models import UnitOfMeasure, UtilityService, Tariff, TariffCell, Counter, CounterReadings
from appartments.models import House, Section, Appartment
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
    

# ------------------------------------------------------------------------
# -----------------------------COUNTER-CRUD-------------------------------
# ------------------------------------------------------------------------
class CounterListView(TemplateView):
    template_name = "utility_services/counter_list.html"

    def get(self, request, *args, **kwargs):

        Q_list = []

        # get sections and floors data from dropboxes
        if self.request.is_ajax() and self.request.method == 'GET' and self.request.GET.get('choosen_house') != None:
            house_data = House.objects.get(title=self.request.GET.get('choosen_house'))
            section_data = list(house_data.sections.values('id', 'title'))
            data = {'section_data': section_data}
            return JsonResponse(data)
        
        if request.GET.get('columns[0][search][value]'):
            if request.GET.get('columns[0][search][value]') != 'all_houses':
                Q_list.append(Q(appartment__house__id=request.GET.get('columns[0][search][value]')))


        if request.GET.get('columns[1][search][value]'):
            if request.GET.get('columns[1][search][value]') != 'empty_sect':
                choosed_section = Section.objects.get(id=request.GET.get('columns[1][search][value]'))
                Q_list.append(Q(appartment__sections=choosed_section))


        if request.GET.get('columns[2][search][value]'):
            if request.GET.get('columns[2][search][value]'):
                number = request.GET.get('columns[2][search][value]')
                Q_list.append(Q(appartment__number__icontains=number))


        if request.GET.get('columns[3][search][value]'):
            if request.GET.get('columns[3][search][value]'):
                title = request.GET.get('columns[3][search][value]')
                Q_list.append(Q(title__icontains=title))


        # datatables serverside logic
        if self.request.is_ajax() and self.request.method == 'GET':
            counter_get_request = request.GET


            # initial data
            draw = int(counter_get_request.get("draw"))
            start = int(counter_get_request.get("start"))
            length = int(counter_get_request.get("length"))

    #         # order logic
    #         order_column_task = 'number'
    #         if appartments_data_get_request.get('order[0][column]'):
    #             number_column = appartments_data_get_request.get('order[0][column]')
    #             order_column_task = appartments_data_get_request.get(f'columns[{number_column}][name]')
    #             if appartments_data_get_request.get('order[0][dir]') == 'desc':
    #                 order_column_task = f"-{order_column_task}"

            # raw_data = Tariff.objects.all()
            raw_data = Counter.objects.filter(*Q_list)\
                                .only('appartment__house__title',\
                                        'appartment__sections__title',\
                                        'appartment__number',\
                                        'title',\
                                        'appartment__sections',\
                                        'counter_reading__date',\
                                        'unit_of_measure__title')\
                                .order_by()\
                                .values('appartment__house__title',\
                                        'appartment__sections__title',\
                                        'appartment__number',\
                                        'title',\
                                        'counter_reading__date',\
                                        'unit_of_measure__title',\
                                        'appartment_id',)

            data = list(raw_data)

    #         # paginator here
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
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['houses'] = House.objects.all()
        return context
    

class CounterReadingsPerAppartmentListView(TemplateView):
    template_name = "utility_services/counter_readings_per_appartment_list.html"
    appartment_id = None


    def get(self, request, *args, **kwargs):

        print('----------------------------')
        print(self.appartment_id)
        print('----------------------------')

        Q_list = []
        Q_list.append(Q(counter__appartment__id=self.__class__.appartment_id))
        

        if request.GET.get('columns[0][search][value]'):
            Q_list.append(Q(id=request.GET.get('columns[0][search][value]')))


        if request.GET.get('columns[1][search][value]'):
            if request.GET.get('columns[1][search][value]') != 'all_status':
                choosed_status = request.GET.get('columns[1][search][value]')
                Q_list.append(Q(status=choosed_status))

        if request.GET.get('columns[2][search][value]'):
            # choosed_status = request.GET.get('columns[2][search][value]')
            date_list = request.GET.get('columns[2][search][value]').split('-')
            start_date = date_list[0].strip().split('.')
            finish_date = date_list[1].strip().split('.')
            # test = start_date.reverse() 
            start_date.reverse()
            finish_date.reverse()

            start_date_string = ''
            finish_date_string = ''
            
            start_date_string = '-'.join(str(elem) for elem in start_date)
            finish_date_string = '-'.join(str(elem) for elem in finish_date)

            formated_date_start = datetime.strptime(start_date_string, '%Y-%m-%d')
            formated_date_finish = datetime.strptime(finish_date_string, '%Y-%m-%d')
            Q_list.append(Q(date__gte=formated_date_start))
            Q_list.append(Q(date__lte=formated_date_finish))
 

        if request.GET.get('columns[4][search][value]'):
            if request.GET.get('columns[4][search][value]') != 'all_houses':
                Q_list.append(Q(counter__appartment__house__id=request.GET.get('columns[4][search][value]')))


        if request.GET.get('columns[5][search][value]'):
            if request.GET.get('columns[5][search][value]') != 'empty_sect':
                # print(request.GET.get('columns[5][search][value]'))
                choosed_section = Section.objects.get(id=request.GET.get('columns[5][search][value]'))
                Q_list.append(Q(counter__appartment__sections=choosed_section))


        if request.GET.get('columns[6][search][value]'):
            if request.GET.get('columns[6][search][value]'):
                number = request.GET.get('columns[6][search][value]')
                Q_list.append(Q(counter__appartment__number__icontains=number))


        if request.GET.get('columns[7][search][value]'):
            if request.GET.get('columns[7][search][value]') != 'all_counter':
                if request.GET.get('columns[7][search][value]'):
                    counter_id = request.GET.get('columns[7][search][value]')
                    Q_list.append(Q(counter__id=counter_id))

    #     # datatables serverside logic
        if self.request.is_ajax() and self.request.method == 'GET':
            counter_per_appartment_get_request = request.GET


    #         # initial data
            draw = int(counter_per_appartment_get_request.get("draw"))
            start = int(counter_per_appartment_get_request.get("start"))
            length = int(counter_per_appartment_get_request.get("length"))

    # #         # order logic
    # #         order_column_task = 'number'
    # #         if appartments_data_get_request.get('order[0][column]'):
    # #             number_column = appartments_data_get_request.get('order[0][column]')
    # #             order_column_task = appartments_data_get_request.get(f'columns[{number_column}][name]')
    # #             if appartments_data_get_request.get('order[0][dir]') == 'desc':
    # #                 order_column_task = f"-{order_column_task}"

            # raw_data = Tariff.objects.all()

            raw_data = CounterReadings.objects\
                                .annotate(date_with_month_year = F('date'))\
                                .filter(*Q_list)\
                                .only('id',\
                                        'counter__appartment__id',\
                                        'status',\
                                        'date',\
                                        'counter__appartment__house__id',\
                                        'counter__appartment__house__title',\
                                        'counter__appartment__sections',\
                                        'counter__appartment__sections__title',\
                                        'counter__appartment__number',\
                                        'counter__id'
                                        'counter__title',
                                        'readings',
                                        'counter__unit_of_measure__title')\
                                .order_by()\
                                .values('id',\
                                        'status',\
                                        'date',\
                                        'counter__appartment__house__title',\
                                        'counter__appartment__sections__title',\
                                        'counter__appartment__number',\
                                        'counter__title',
                                        'readings',
                                        'counter__unit_of_measure__title',\
                                        'date_with_month_year')
            # print(raw_data)

            verbose_status_dict = CounterReadings.get_verbose_status_dict()
            data = list(raw_data)

            for readings in data:
                date_per_month = readings['date_with_month_year']
                new_date = format_date(date_per_month, 'LLLL Y', locale='ru')
                readings['date_with_month_year'] = new_date

                verbose_status = ""
                try: 
                    verbose_status = verbose_status_dict[readings['status']]
                    readings['status'] = verbose_status
                except:
                    readings['status'] = ''
                
                simple_date = readings['date']
                new_simple_date = format_date(simple_date, 'dd.MM.yyyy', locale='ru')
                readings['date'] = new_simple_date



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
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['houses'] = House.objects.all()

        self.__class__.appartment_id = self.kwargs['pk']

        context['appartment'] = Appartment.objects.get(id=self.__class__.appartment_id)        
        context['counters'] = Counter.objects.all()
        return context




# class AddCounterReadingsView(CreateView):
#     template_name = 'utility_services/tariff_edite.html'
#     form_class = TariffMainForm
#     model = Tariff
#     success_url = reverse_lazy('utility_services:tariff_list')

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['tariff_cell_formset'] = CreateTariffCellFormSet(prefix="tariff_cell")
    #     return context

    # def get(self, request, *args, **kwargs):
    #     if self.request.is_ajax() and self.request.method == 'GET' and self.request.GET.get('choosen_utility_service') != None:
    #         service_id = self.request.GET['choosen_utility_service']
    #         service = UtilityService.objects.get(id=service_id)
    #         unit_measure = service.unit_of_measure.title
    #         response = {'unit_measure': unit_measure}
    #         return JsonResponse(response, safe=False)
    #     else:
    #         return super().get(request, *args, **kwargs)
    
    # def post(self, request, *args, **Kwargs):
    #     tariff_form = TariffMainForm(request.POST)
    #     tariff_cell_formset = CreateTariffCellFormSet(request.POST, prefix="tariff_cell")
    #     if tariff_form.is_valid() and tariff_cell_formset.is_valid():
    #         return self.form_valid(tariff_form, tariff_cell_formset)
    #     else:
    #         if tariff_cell_formset.errors:
    #             for tariff_cell in tariff_cell_formset:
    #                 for field, error in tariff_cell.errors.items():
    #                     print(f'{field}: {error}')

        
    # def form_valid(self, tariff_form, tariff_cell_formset):
    #     tariff = tariff_form.save(commit=False)
    #     tariff.save()
    #     for tariff_cell in tariff_cell_formset:
    #         cell = tariff_cell.save(commit=False)
    #         cell.tariff = tariff
    #         cell.save()
    #     tariff.updated_datetime = datetime.now()
    #     tariff.save()
    #     success_url = self.success_url
    #     messages.success(self.request, f"Создан тариф {tariff_form.instance.title}.")
    #     return HttpResponseRedirect(success_url)