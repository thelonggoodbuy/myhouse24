from django.shortcuts import render
from django.db.models import F, Q, CharField, Value, Sum
import operator
from functools import reduce
from datetime import datetime, date
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models.functions import Concat
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect, JsonResponse
from babel.dates import format_date
import calendar
from django.urls import reverse_lazy
from django.contrib import messages

from django.views.generic.base import TemplateView


from users.models import User
from appartments.models import House, Section, Appartment, PersonalAccount
from utility_services.models import Tariff, TariffCell, CounterReadings
from .models import Receipt
from .forms import AddReceiptForm, UtilityReceiptForm, ReceiptCellFormset



class CRMReportView(TemplateView):
    
    template_name = "receipts/crm_report.html"



class ReceiptListView(TemplateView):
    template_name = 'receipts/receipt_list.html'

    def get(self, request, *args, **kwargs):


        # SELECT2 logic
        if self.request.is_ajax() and self.request.GET.get('issue_marker') == 'owners':
            if self.request.GET.get('search'):
                search_data = self.request.GET.get('search')
                owners_data = list(User.objects.filter(full_name__icontains=search_data).values('id', 'full_name'))
                for owner_dict in owners_data: owner_dict['text'] = owner_dict.pop('full_name')
                data = {'results': owners_data}
                return JsonResponse(data)
                

        # users search using Select2
        if self.request.is_ajax() and self.request.GET.get('issue_marker') == 'all_owners':
            owners_data = list(User.objects.all().values('id', 'full_name'))
            for owner_dict in owners_data: owner_dict['text'] = owner_dict.pop('full_name')
            data = {'results': owners_data}
            return JsonResponse(data)



       # datatables serverside logic
        if self.request.is_ajax() and self.request.method == 'GET' and request.GET.get('draw'):
            receipt_data_get_request = request.GET

            #search logic 
            Q_list = []

            # number filtering
            if request.GET.get('columns[1][search][value]'):
                Q_list.append(Q(number__icontains=request.GET.get('columns[1][search][value]')))

            # status filtering
            if request.GET.get('columns[2][search][value]'):
                print(request.GET.get('columns[2][search][value]'))
                if request.GET.get('columns[2][search][value]') != 'all_status':
                    Q_list.append(Q(status=request.GET.get('columns[2][search][value]')))

            # date range search
            if request.GET.get('columns[3][search][value]'):

                date_list = request.GET.get('columns[3][search][value]').split('-')

                start_date = date_list[0].strip().split('.')
                finish_date = date_list[1].strip().split('.')
                start_date.reverse()
                finish_date.reverse()

                start_date_string = ''
                finish_date_string = ''
                
                start_date_string = '-'.join(str(elem) for elem in start_date)
                finish_date_string = '-'.join(str(elem) for elem in finish_date)

                formated_date_start = datetime.strptime(start_date_string, '%Y-%m-%d')
                formated_date_finish = datetime.strptime(finish_date_string, '%Y-%m-%d')
                Q_list.append(Q(to_date__gte=formated_date_start))
                Q_list.append(Q(to_date__lte=formated_date_finish))

            # date with month and year
            if request.GET.get('columns[4][search][value]'):
                date_list = request.GET.get('columns[4][search][value]').split('.')
                month = int(date_list[0])
                year = int(date_list[1])
                first_last_day = calendar.monthrange(year, month)
                first_day = date(year, month, 1)
                last_day = date(year, month, first_last_day[1])
                Q_list.append(Q(date_with_month_year__gte=first_day))
                Q_list.append(Q(date_with_month_year__lte=last_day))

            # full address filter
            if request.GET.get('columns[5][search][value]'):
                search_address_list_parameter = list((request.GET.get('columns[5][search][value]').strip()).split(" "))
                Q_list.append(reduce(operator.and_, (Q(appartments_address__icontains=part_addr) for part_addr in search_address_list_parameter)))

            # full name of owner
            if request.GET.get('columns[6][search][value]'):
                print('----------------------------')
                print(request.GET.get('columns[6][search][value]'))
                print('----------------------------')
                if request.GET.get('columns[6][search][value]'):
                    print(request.GET.get('columns[6][search][value]'))
                    user = User.objects.get(id=request.GET.get('columns[6][search][value]'))
                    Q_list.append(Q(appartment__owner_user=user))


            # payment status filter
            if request.GET.get('columns[7][search][value]'):
                if request.GET.get('columns[7][search][value]') != 'all_payment_status':
                    Q_list.append(Q(payment_was_made=request.GET.get('columns[7][search][value]')))



            draw = int(receipt_data_get_request.get("draw"))
            start = int(receipt_data_get_request.get("start"))
            length = int(receipt_data_get_request.get("length"))

            raw_data = Receipt.objects.annotate(appartments_address = ArrayAgg(Concat(F('appartment__number'),
                                                                                    Value(', '),
                                                                                    F('appartment__house__title'),
                                                                                    output_field=CharField())
                                                                                    ,distinct=True))\
                                    .annotate(date_with_month_year = F('to_date'))\
                                    .filter(*Q_list)\
                                    .order_by('-to_date')\
                                    .values('number', 'status', 'to_date',\
                                            'date_with_month_year', 'appartments_address',\
                                            'appartment__owner_user__full_name',\
                                            'payment_was_made', 'total_sum', "id")

            data = list(raw_data)
            verbose_status_dict = Receipt.get_verbose_status_dict()

            for receipt in data:  
                verbose_status = ""
                try: 
                    verbose_status = verbose_status_dict[receipt['status']]
                    receipt['status'] = verbose_status
                except:
                    receipt['status'] = ''


                simple_date = receipt['to_date']
                new_simple_date = format_date(simple_date, 'dd.MM.yyyy', locale='ru')
                receipt['to_date'] = new_simple_date

                date_per_month = receipt['date_with_month_year']
                new_date = format_date(date_per_month, 'LLLL Y', locale='ru')
                receipt['date_with_month_year'] = new_date

                payment_status = receipt['payment_was_made']
                if payment_status == True:
                    receipt['payment_was_made'] = 'Проведена'
                else:
                    receipt['payment_was_made'] = 'Не проведена'



            # paginator here
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
        return context



# class AddCounterReadingsView(CreateView):
class AddReceiptView(TemplateView):

    template_name = 'receipts/receipt_create.html'    
    form_class = AddReceiptForm
    model = Receipt
    success_url = reverse_lazy('receipts:receipt_list')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['main_form'] = AddReceiptForm(prefix='main_form')
        context['utility_form'] = UtilityReceiptForm(prefix='utility_form')
        context['receipt_cell_formset'] = ReceiptCellFormset(prefix='receipt_cell_formset')

        return context


    def get(self, request, *args, **kwargs):
        
        if self.request.is_ajax() and self.request.method == 'GET' and self.request.GET.get('ajax_indicator') == 'get_certain_house':
            house_id = self.request.GET['current_house_number']
            house = House.objects.get(id=house_id)
            sections = list(Section.objects.only('id', 'title').filter(house=house).values('id', 'title'))
            appartments = list(Appartment.objects.only('id', 'number').filter(house=house).values('id', 'number'))
            response = {'sections': sections,
                        'appartments':appartments}
            return JsonResponse(response, safe=False)

        if self.request.is_ajax() and self.request.method == 'GET' and self.request.GET.get('ajax_indicator') == 'get_appartments_per_sections':
            sections_id = self.request.GET.get('current_sections_number')
            choosen_sections = Section.objects.get(id=sections_id)
            appartments = list(Appartment.objects.only('id', 'number').filter(sections=choosen_sections).values('id', 'number'))
            response = {'appartments':appartments}
            return JsonResponse(response, safe=False)
        
        if self.request.is_ajax() and self.request.method == 'GET' and self.request.GET.get('ajax_indicator') == 'get_personal_account_per_appartment':
            appartment_id = self.request.GET.get('appartment')
            choosen_personal_account = list(PersonalAccount.objects.filter(appartment_account__id=appartment_id)\
                                            .values('id', 'number', 'appartment_account__owner_user__full_name',\
                                                    'appartment_account__owner_user__id','appartment_account__owner_user__phone'))
            response = {'personal_account': choosen_personal_account}
            return JsonResponse(response, safe=False)
        
        if self.request.is_ajax() and self.request.method == 'GET' and self.request.GET.get('ajax_indicator') == 'add_all_utilities_using_tariff':
            tariff_id = self.request.GET.get('tariff_id')
            tariff_cell_data = list(TariffCell.objects.filter(tariff__id=tariff_id)\
                                            .values('utility_service__id', 'utility_service__unit_of_measure__id', 'cost_per_unit'))
            response = {'tariff_cell_data': tariff_cell_data}
            return JsonResponse(response, safe=False)

        if self.request.is_ajax() and self.request.method == 'GET' and self.request.GET.get('ajax_indicator') == 'add_counters_readings_per_appartment':
            appartment_id = self.request.GET.get('appartment_id')

            counter_tariff_cell_data = list(CounterReadings.objects.filter(counter__appartment__id=appartment_id)\
                                            .values('counter__id', 'counter__unit_of_measure__id', 'readings', 'id'))
            response = {'tariff_cell_data': counter_tariff_cell_data}
            return JsonResponse(response, safe=False)


        else:
            return super().get(request, *args, **kwargs)


    def post(self, request, *args, **Kwargs):
        main_form = AddReceiptForm(request.POST, prefix='main_form')        
        receipt_cell_formset = ReceiptCellFormset(request.POST, prefix='receipt_cell_formset')
        if main_form.is_valid() and receipt_cell_formset.is_valid():
            return self.form_valid(main_form, receipt_cell_formset)
        else:

            if main_form.errors:
                for field, error in main_form.errors.items():
                    print(f'{field}: {error}')

            if receipt_cell_formset.errors:
                for receipt_form in receipt_cell_formset:
                    for field, error in receipt_form.errors.items():
                        print(f'{field}: {error}')

        
    def form_valid(self, main_form, receipt_cell_formset):
        mainform_instance = main_form.save()
        # main_form.save()
        # receipt_cell_formset.save()
        for receipt_cell_form in receipt_cell_formset:
            receipt_cell = receipt_cell_form.save(commit=False)
            receipt_cell.receipt = mainform_instance
            receipt_cell.save()
        # receipt_cell_formset.save()
        success_url = self.success_url
        messages.success(self.request, f"Квитанция создана!")
        return HttpResponseRedirect(success_url)