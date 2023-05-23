from django.shortcuts import render
from datetime import datetime
from django.views.generic.base import TemplateView
from .models import MastersRequest
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models.functions import Concat
from django.db.models import F, Q, CharField, Value
import operator
from functools import reduce
from django.http import HttpResponseRedirect


from users.models import User
from django.views.generic.edit import FormView, UpdateView, DeleteView
from .forms import MastersRequestsCreateForm
from django.urls import reverse_lazy
from django.contrib import messages
from appartments.models import Appartment
from .models import MastersRequest


class MastersRequestsListView(TemplateView):
    template_name = 'masters_services/masters_requests_list.html'

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
            owners_data = list(User.objects.filter(owning__isnull=False).values('id', 'full_name'))
            for owner_dict in owners_data: owner_dict['text'] = owner_dict.pop('full_name')
            data = {'results': owners_data}
            return JsonResponse(data)


        # datatables serverside logic

        if self.request.is_ajax() and self.request.method == 'GET' and request.GET.get('draw'):
            masters_get_request = request.GET

            #search logic 
            Q_list = []

            if request.GET.get('columns[0][search][value]'):
                Q_list.append(Q(id__icontains=request.GET.get('columns[0][search][value]')))

            if request.GET.get('columns[1][search][value]'):
                date_list = request.GET.get('columns[1][search][value]').split('-')

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
                Q_list.append(Q(date_work__gte=formated_date_start))
                Q_list.append(Q(date_work__lte=formated_date_finish))


            if request.GET.get('columns[2][search][value]'):
                if request.GET.get('columns[2][search][value]') != 'all_master_types':
                    Q_list.append(Q(master_type=request.GET.get('columns[2][search][value]')))


            if request.GET.get('columns[3][search][value]'):
                Q_list.append(Q(description__icontains=request.GET.get('columns[3][search][value]')))


            if request.GET.get('columns[4][search][value]'):
                if request.GET.get('columns[4][search][value]'):
                    search_address_list_parameter = list((request.GET.get('columns[4][search][value]').strip()).split(" "))
                    Q_list.append(reduce(operator.and_, (Q(appartment_data__icontains=part_addr) for part_addr in search_address_list_parameter)))


            if request.GET.get('columns[5][search][value]'):
                if request.GET.get('columns[5][search][value]'):
                    user = User.objects.get(id=request.GET.get('columns[5][search][value]'))
                    Q_list.append(Q(appartment__owner_user=user))


            if request.GET.get('columns[6][search][value]'):
                Q_list.append(Q(appartment__owner_user__phone__icontains=request.GET.get('columns[6][search][value]')))


            if request.GET.get('columns[7][search][value]'):
                Q_list.append(Q(master__id=request.GET.get('columns[7][search][value]')))


            if request.GET.get('columns[8][search][value]'):
                Q_list.append(Q(status=request.GET.get('columns[8][search][value]')))

            # initial data
            draw = int(masters_get_request.get("draw"))
            start = int(masters_get_request.get("start"))
            length = int(masters_get_request.get("length"))

            # order logic
            order_column_task = 'number'
            if masters_get_request.get('order[0][column]'):
                number_column = masters_get_request.get('order[0][column]')
                order_column_task = masters_get_request.get(f'columns[{number_column}][name]')
                if masters_get_request.get('order[0][dir]') == 'desc':
                    order_column_task = f"-{order_column_task}"

            
            raw_data = MastersRequest.objects.annotate(date_and_time = ArrayAgg(Concat(
                                                                                    F('date_work'),
                                                                                    Value(':'),
                                                                                    F('time_work'),
                                                                                    output_field=CharField())
                                                                                    ,distinct=True))\
                                            .annotate(appartment_data = ArrayAgg(Concat(Value('кв.'),
                                                                                    F('appartment__number'),
                                                                                    Value(', '),
                                                                                    F('appartment__house__title'),
                                                                                    output_field=CharField())
                                                                                    ,distinct=True))\
                                                                .filter(*Q_list)\
                                                                .only('id', 'master_type', 'description',\
                                                                       'appartment__owner_user__full_name',\
                                                                        'appartment__owner_user__phone',\
                                                                        'master__full_name', 'status', 'appartment__id',\
                                                                        'appartment__owner_user__id')\
                                                                .order_by(order_column_task)\
                                                                .values('id', 'date_and_time', 'master_type', 'description',\
                                                                        'appartment_data', 'appartment__owner_user__full_name',\
                                                                        'appartment__owner_user__phone',\
                                                                        'master__full_name', 'status', 'appartment__id',\
                                                                        'appartment__owner_user__id')

            data = list(raw_data)

            request_dictionary = MastersRequest.get_request_to_dictionary()
            status_deictionary = MastersRequest.get_status_dictionary()

            for cell in data:
                date_and_time = cell['date_and_time']
                date = date_and_time[0].strip()[:10].split('-')
                time = date_and_time[0].strip()[11:16]
                date.reverse()
                date_string = '.'.join(str(elem) for elem in date)
                cell['date_and_time'] = f'{date_string} - {time}'

                worker_type = cell['master_type']
                cell['master_type'] = request_dictionary[worker_type]

                request_status = cell['status']
                cell['status'] = status_deictionary[request_status]


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
        context['masters'] = User.objects.filter(Q(role__isnull=False) and Q(masters_request__isnull=False))
        return context
    


class MastersRequestsCreateView(FormView):
    template_name = "masters_services/masters_requests_create.html"
    form_class = MastersRequestsCreateForm
    success_url = reverse_lazy('masters_services:masters_requests_list')


    def get(self, request, *args, **kwargs):        

        # select 2 owners data
        if self.request.is_ajax() and self.request.method == 'GET' and self.request.GET.get('issue_marker') == 'owner_marker':
            if self.request.GET.get('search'):
                search_data = self.request.GET.get('search')
                owners_Q_list = []
                search_full_name_list_parameter = list((search_data.strip()).split(" "))
                owners_Q_list.append(reduce(operator.and_, (Q(full_name__icontains=part_name) for part_name in search_full_name_list_parameter)))
                owners_Q_list.append(Q(owning__isnull=False))
                owners_data = list(User.objects.filter(*owners_Q_list).distinct().values('id', 'full_name'))
                for owner_dict in owners_data: owner_dict['text'] = owner_dict.pop('full_name')
                data = {'results': owners_data}
                return JsonResponse(data)


        if self.request.is_ajax() and self.request.method == 'GET' and self.request.GET.get('issue_marker') == 'all_owners_marker':
            owners_data = list(User.objects.filter(owning__isnull=False).distinct().values('id', 'full_name'))
            for owner_dict in owners_data: owner_dict['text'] = owner_dict.pop('full_name')
            data = {'results': owners_data}
            return JsonResponse(data)
        # end select 2 owners data

        # select 2 appartments data
        if self.request.is_ajax() and self.request.method == 'GET' and self.request.GET.get('issue_marker') == 'appartment_marker':
            if self.request.GET.get('search'):
                search_data = self.request.GET.get('search')
                appartment_Q_list = []
                appartment_Q_list.append(Q(owner_user__isnull=False))
                appartment_Q_list.append(Q(number_incontains=search_data))
                if self.request.GET.get('choosen_owner_id'): appartment_Q_list.append(Q(owner_user__id=self.request.GET.get('choosen_owner_id')))
                appartment_data = list(Appartment.objects.filter(*appartment_Q_list).distinct().values('id', 'number', 'house__title'))
                for apartment_dict in appartment_data: apartment_dict['text'] = f"{apartment_dict.pop('number'), apartment_dict.pop('house__title')}"
                data = {'results': appartment_data}
                print(data)
                return JsonResponse(data)
            
        if self.request.is_ajax() and self.request.method == 'GET' and self.request.GET.get('issue_marker') == 'all_apartments_marker':
            appartment_Q_list = []
            appartment_Q_list.append(Q(owner_user__isnull=False))
            if self.request.GET.get('choosen_owner_id'): appartment_Q_list.append(Q(owner_user__id=self.request.GET.get('choosen_owner_id')))
            appartment_data = list(Appartment.objects.filter(*appartment_Q_list).distinct().values('id', 'number', 'house__title'))
            for apartment_dict in appartment_data: apartment_dict['text'] = f"{apartment_dict.pop('number')}, {apartment_dict.pop('house__title')}"
            data = {'results': appartment_data}
            print(data)
            return JsonResponse(data)
        # end select 2 appartments data

        else:
            context = self.get_context_data(**kwargs)
            return self.render_to_response(context)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)     
        context['masters_request_form'] = MastersRequestsCreateForm(prefix="masters_request_form")
        return context
    

    def post(self, request, *args, **Kwargs):
        masters_request_form = MastersRequestsCreateForm(request.POST, prefix="masters_request_form")
        if masters_request_form.is_valid():
            return self.form_valid(masters_request_form)
        else:
            if masters_request_form.errors:
                for field, error in masters_request_form.errors.items():
                    print(f'{field}: {error}')


    def form_valid(self, masters_request_form):
        masters_request_form.save()
        success_url = self.success_url
        messages.success(self.request, f"Запрос на услуги мастера создан!")
        return HttpResponseRedirect(success_url)
    

class MastersRequestsEditeView(UpdateView):
    form_class = MastersRequestsCreateForm
    model = MastersRequest
    template_name = 'masters_services/masters_requests_create.html'
    success_url = reverse_lazy('masters_services:masters_requests_list')
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['masters_request_form'] = MastersRequestsCreateForm(instance=self.get_object(), prefix="masters_request_form")
        return context
    
    def get(self, request, *args, **kwargs):
        if self.request.is_ajax() and self.request.method == 'GET' and self.request.GET.get('issue_marker') == 'get_owner_marker':
            appartment_id = self.request.GET['current_appartment']
            user_data = list(User.objects.filter(owning__id=appartment_id).values('id', 'full_name'))
            response = {'user_initial_data': user_data}
            return JsonResponse(response, safe=False)
        else:
            self.object = self.get_object()
            return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **Kwargs):
        masters_request_form = MastersRequestsCreateForm(request.POST, instance=self.get_object(), prefix="masters_request_form")
        if masters_request_form.is_valid():
            return self.form_valid(masters_request_form)
        else:
            if masters_request_form.errors:
                for tariff_cell in masters_request_form:
                    for field, error in tariff_cell.errors.items():
                        print(f'{field}: {error}')

        
    def form_valid(self, masters_request_form):
        masters_request_form.save()
        success_url = self.success_url
        messages.success(self.request, f"Данные о запросе № { masters_request_form.instance.id } обновлены.")
        return HttpResponseRedirect(success_url)



class MastersRequestsDeleteView(DeleteView):

    model = MastersRequest
    success_url = reverse_lazy('masters_services:masters_requests_list')
    
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)