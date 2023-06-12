from copy import deepcopy
import operator
from functools import reduce
from django import forms
from general_statistics.models import GraphTotalStatistic



from django.db import models
from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import F, Q, OuterRef, Subquery, CharField, Value, Count, Sum, DecimalField
from django.http import HttpResponseRedirect, JsonResponse
from datetime import datetime
from django.utils.dateformat import DateFormat
from django.db.models import Prefetch
from django.contrib.postgres.aggregates import ArrayAgg, StringAgg
from django.db.models.functions import Concat

from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.views.generic.edit import DeleteView, FormView, UpdateView, CreateView

from django.views.generic.detail import DetailView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ImproperlyConfigured

from .models import House, HouseAdditionalImage, Section, Appartment, Floor, PersonalAccount
from users.models import User
from utility_services.models import Tariff

from .forms import HouseEditeForm, HouseEditeFormSetImage, SectionEditeFormSet, FloorEditeFormSet, ResponsibilitiesEditeFormset,\
                    AppartmentEditeForm, OwnerUpdateForm, AppartmentTariffForm, AppartmentTariffForset, PersonalAccountCreateForm,\
                    SendOwnderForm, AppartmentCreateForm
from general_statistics.models import GraphTotalStatistic

# view for testing role using
class ReportView(TemplateView):
    
    template_name = "appartments/cabinet_report_per_appartment.html"

# ------------------------------------------------------------------
# -----------------Houses CRUID-------------------------------------
# ------------------------------------------------------------------
class HousesListView(ListView):
    model = House
    context_object_name = 'houses_list'
    template_name = 'appartments/houses_list.html'


class HouseDeleteView(DeleteView):

    model = House
    success_url = reverse_lazy('appartments:houses_list')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        house_title = self.object.title
        success_url = self.get_success_url()
        self.object.delete()
        messages.success(request, (f"Дом  '{ house_title }'. Удален."))
        return HttpResponseRedirect(success_url)
    


class HouseEditeView(UpdateView):
    form_class = HouseEditeForm
    model = House
    template_name = "appartments/house_edit.html"
    success_url = reverse_lazy('appartments:houses_list')
   
    initial_responsibility = []

    def get(self, request, *args, **kwargs):
        if self.request.is_ajax() and self.request.method == 'GET':
            # print(self.request.GET['choosen_user'])
            user_id = self.request.GET['choosen_user']
            user = User.objects.get(id=user_id)
            user_role = user.role.name
            response = {'user_id': user_role}
            print(response)
            return JsonResponse(response, safe=False)
        else:
            self.object = self.get_object()
            return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        additiona_images = HouseAdditionalImage.objects.select_related('house').filter(house=self.object)
        context['simple_images_formset'] = HouseEditeFormSetImage(queryset=additiona_images, prefix='simple_images_formset')
        context['section_formset'] = SectionEditeFormSet(instance=self.get_object(), prefix="section_formset")
        context['floor_formset'] = FloorEditeFormSet(instance=self.get_object(), prefix="floor_formset")

        self.__class__.initial_responsibility = []
        for responsibility in self.object.responsibilities.filter(Q(role__isnull=False)): 
            self.__class__.initial_responsibility.append({'responsibilities': responsibility, 'role': responsibility.role})
        context['responsibilities_formset'] = ResponsibilitiesEditeFormset(initial=self.__class__.initial_responsibility, prefix="responsibility_formset")
        return context

    def post(self, request, *args, **Kwargs):
        main_form = HouseEditeForm(request.POST, request.FILES, instance=self.get_object())
        addition_images_formset = HouseEditeFormSetImage(request.POST, request.FILES, queryset=HouseAdditionalImage.objects.filter(house=self.get_object()), prefix='simple_images_formset')
        sections_formset = SectionEditeFormSet(request.POST, instance=self.get_object(), prefix="section_formset")
        floor_formset = FloorEditeFormSet(request.POST, instance=self.get_object(), prefix="floor_formset")
        responsibilities_formset = ResponsibilitiesEditeFormset(request.POST, initial=self.__class__.initial_responsibility, prefix="responsibility_formset")

        if main_form.is_valid()\
                            and addition_images_formset.is_valid()\
                            and sections_formset.is_valid()\
                            and floor_formset.is_valid()\
                            and responsibilities_formset.is_valid():
            
            return self.form_valid(main_form,\
                                addition_images_formset,\
                                sections_formset,\
                                floor_formset,\
                                responsibilities_formset)
        else:
            print('------------------------SMTH WRONG-----------------------')
            print(main_form.errors)
            print(addition_images_formset.errors)
            print(sections_formset.errors)
            print(responsibilities_formset.errors)

    def form_valid(self,\
                main_form,\
                addition_images_formset,\
                sections_formset,\
                floor_formset,\
                responsibilities_formset):
        
        house = main_form.save(commit=False)
        house_images_formset = addition_images_formset.save(commit=False)

        for image in house_images_formset:
            image.house = house
            image.save()
        
        sections_formset.save()

        floor_formset.save()

        responsibility_queryset = []
        for responsibility in responsibilities_formset:
            if responsibility.cleaned_data.get('DELETE') == True:
              house.responsibilities.remove(responsibility.cleaned_data.get('responsibilities'))
            else: 
                choosen_user = responsibility.cleaned_data.get('responsibilities')
                # print(choosen_user)
                if choosen_user != None: responsibility_queryset.append(choosen_user)
        house.responsibilities.set(responsibility_queryset)        

        house.save()
        success_url = self.success_url
        messages.success(self.request, f"Данные о доме {self.get_object().title} обновлены.")
        return HttpResponseRedirect(success_url)
    

class HouseDetailView(DetailView):
    queryset = House.objects.select_related().all()
    template_name = "appartments/house_detail.html"
    context_object_name = 'house'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)     
        context['responsibility_users'] = self.get_object().responsibilities.select_related('role').filter()
        return context
    
# ------------------------------------------------------------------
# -----------------Appartments CRUID--------------------------------
# ------------------------------------------------------------------
class AppartmentsListView(TemplateView):
    template_name = 'appartments/appartments_list.html'

    def get(self, request, *args, **kwargs):

        # get sections and floors data from dropboxes
        if self.request.is_ajax() and self.request.method == 'GET' and self.request.GET.get('choosen_house') != None:
            house_data = House.objects.get(title=self.request.GET.get('choosen_house'))
            section_data = list(house_data.sections.values('id', 'title'))
            floors_data = list(house_data.floors.values('id', 'title'))
            data = {'section_data': section_data,
                    'floors_data': floors_data}
            return JsonResponse(data)

        # get data owners and users
        if self.request.is_ajax() and self.request.method == 'GET' and self.request.GET.get('target') == 'get_choose_owners_data':
            print('----------------------------USER-OWNER-FILTER------------------------')
            owners_dict = list(User.objects.filter(owning__isnull=False).values('id', 'full_name'))
            data = {'owners_dict': owners_dict}
            return JsonResponse(data)

        # test code for ajax_requests
        if self.request.is_ajax() and self.request.GET.get('issue_marker') == 'owners':
            if self.request.GET.get('search'):
                search_data = self.request.GET.get('search')
                owners_data = list(User.objects.filter(Q(owning__isnull=False) & Q(full_name__icontains=search_data)).values('id', 'full_name'))
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
        if self.request.is_ajax() and self.request.method == 'GET':
            appartments_data_get_request = request.GET

            #search logic 
            Q_list = []

            if request.GET.get('columns[0][search][value]'):
                Q_list.append(Q(number=request.GET.get('columns[0][search][value]')))

            if request.GET.get('columns[1][search][value]'):
                print('----------------------------HOUSE-FILTER------------------------')
                if request.GET.get('columns[1][search][value]') != 'all_houses':
                    chooset_house = House.objects.get(id=request.GET.get('columns[1][search][value]'))
                    Q_list.append(Q(house=chooset_house))
                

            if request.GET.get('columns[2][search][value]'):
                print('----------------------------SECTION-FILTER------------------------')
                if request.GET.get('columns[2][search][value]') != 'empty_sect':
                    choosed_section = Section.objects.get(id=request.GET.get('columns[2][search][value]'))
                    Q_list.append(Q(sections=choosed_section))

            if request.GET.get('columns[3][search][value]'):
                print('-----------------FLOOR-FILTER-----------------------------')
                print(request.GET.get('columns[3][search][value]'))
                if request.GET.get('columns[3][search][value]') != 'empty_floor':
                    print(request.GET.get('columns[3][search][value]'))
                    choose_floor = Floor.objects.get(id=request.GET.get('columns[3][search][value]'))
                    Q_list.append(Q(floor=choose_floor))


            if request.GET.get('columns[4][search][value]'):
                print('----------------------------OWNERS-FILTER------------------------')
                # if request.GET.get('columns[4][search][value]') != 'empty_sect':
                
                if request.GET.get('columns[4][search][value]'):
                    print(request.GET.get('columns[4][search][value]'))
                    user = User.objects.get(id=request.GET.get('columns[4][search][value]'))
                    Q_list.append(Q(owner_user=user))


            if request.GET.get('columns[5][search][value]'):
                print('-----------------BALANCE-FILTER-----------------------------')
                print(request.GET.get('columns[5][search][value]'))
                if request.GET.get('columns[5][search][value]') == 'debt':
                    Q_list.append(Q(personal_account__balance__lt=0))
                elif request.GET.get('columns[5][search][value]') == 'no_debt':
                    Q_list.append(Q(personal_account__balance__gte=0))
                elif request.GET.get('columns[5][search][value]') == 'all_balance':
                    pass


                        # initial data
            draw = int(appartments_data_get_request.get("draw"))
            start = int(appartments_data_get_request.get("start"))
            length = int(appartments_data_get_request.get("length"))

            # order logic
            order_column_task = 'number'
            if appartments_data_get_request.get('order[0][column]'):
                number_column = appartments_data_get_request.get('order[0][column]')
                order_column_task = appartments_data_get_request.get(f'columns[{number_column}][name]')
                if appartments_data_get_request.get('order[0][dir]') == 'desc':
                    order_column_task = f"-{order_column_task}"


            raw_data = Appartment.objects.filter(*Q_list)\
                                .only('number', 'house__title', 'sections__title', 'floor__title', 'owner_user__full_name', 'personal_account__balance', 'id')\
                                .order_by(order_column_task)\
                                .values('number', 'house__title', 'sections__title', 'floor__title', 'owner_user__full_name', 'personal_account__balance', 'id')

            data = list(raw_data)

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
        context['houses'] = House.objects.all()
        return context
    


class AppartmentsCardView(DetailView):
    queryset = Appartment.objects.select_related('personal_account', 'house', 'sections', 'floor', 'owner_user').all()    
    template_name = "appartments/appartments_card.html"
    context_object_name = 'appartment'


class AppartmentDeleteView(DeleteView):

    model = Appartment
    success_url = reverse_lazy('appartments:appartments_list')
    

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        appartment_id = self.object.id
        print(self.get_success_url())
        success_url = self.get_success_url()
        self.object.delete()
        messages.success(request, (f'Квартира с id {appartment_id}. Удален.'))
        return HttpResponseRedirect(success_url)
    

class AppartmentEditeView(UpdateView):

    model = Appartment
    template_name = 'appartments/appartments_edit.html'
    success_url = reverse_lazy('appartments:appartments_list')
    form_class = AppartmentEditeForm
    

    def get(self, request, *args, **kwargs):
        # select 2 filtering owners
        if self.request.is_ajax() and self.request.method == 'GET' and self.request.GET.get('issue_marker') == 'owner_marker':
            if self.request.GET.get('search'):
                search_data = self.request.GET.get('search')
                owners_data = list(User.objects.filter(full_name__icontains=search_data).order_by('-id').values('id', 'full_name'))
                for owner_dict in owners_data: owner_dict['text'] = owner_dict.pop('full_name')
                data = {'results': owners_data}
                return JsonResponse(data)

        # select 2 all owners data
        if self.request.is_ajax() and self.request.method == 'GET' and self.request.GET.get('issue_marker') == 'all_owners_marker':
            owners_data = list(User.objects.all().order_by('-id').values('id', 'full_name'))
            for owner_dict in owners_data: owner_dict['text'] = owner_dict.pop('full_name')
            data = {'results': owners_data}
            return JsonResponse(data)
        


        # select 2 filtering accounts
        if self.request.is_ajax() and self.request.method == 'GET' and self.request.GET.get('issue_marker') == 'account_marker':
            if self.request.GET.get('search'):
                print('-------SEARCHING-----------')
                search_data = self.request.GET.get('search')
                print(f'search data: {search_data}')

                accounts_data = list(PersonalAccount.objects.filter(Q(number__icontains=search_data) or Q(appartment_account__isnull=True))\
                                                                    .values('id', 'number'))
                print(accounts_data)
                for account_dict in accounts_data: account_dict['text'] = account_dict.pop('number')
                data = {'results': accounts_data}
                return JsonResponse(data)

        # select 2 all accounts data
        if self.request.is_ajax() and self.request.method == 'GET' and self.request.GET.get('issue_marker') == 'all_accounts_marker':
            accounts_data = list(PersonalAccount.objects.filter(appartment_account__isnull=True).values('id', 'number'))
            for account_dict in accounts_data: account_dict['text'] = account_dict.pop('number')
            data = {'results': accounts_data}
            return JsonResponse(data)


        if self.request.method == 'GET' and self.request.GET.get('house_id') != None:
            house_id = self.request.GET.get('house_id')
            house = House.objects.get(id=house_id)
            sections = list(Section.objects.only('id', 'title').filter(house=house).values('id', 'title'))
            floors = list(Floor.objects.only('id', 'title').filter(house=house).values('id', 'title'))
            data = {'sections': sections,
                    'floors': floors}
            return JsonResponse(data)
        
        if self.request.method == 'GET' and self.request.GET.get('issue_marker') == 'initialization_sections_and_floors':
            extra_floors = Floor.objects.exclude(house__id = self.request.GET.get('current_house')).values('id')
            extra_floors_list = []
            for dict in extra_floors: extra_floors_list.append(dict['id'])
            extra_sections = Section.objects.exclude(house__id = self.request.GET.get('current_house')).values('id')
            extra_sections_list = []
            for dict in extra_sections: extra_sections_list.append(dict['id'])
            
            data = {'extra_floors_list': extra_floors_list,
                    'extra_sections_list': extra_sections_list}
            return JsonResponse(data)
        
        else:
            return super().get(request, *args, **kwargs)
        

    def post(self, *args, **kwargs):
        main_form = AppartmentEditeForm(self.request.POST, instance=self.get_object(), prefix='main_form')
        if (main_form.is_valid()):
            return self.form_valid(main_form)
        else: 
            return self.form_invalid(main_form)

    def get_object(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        return self.model.objects.select_related('house', 'sections', 'floor').get(id=pk)



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['main_form'] = AppartmentEditeForm(instance=self.object, prefix='main_form')
        return context



    def form_valid(self, main_form):
        main_form.save()
        messages.success(self.request, 'Квартира обновлена')
        success_url = self.success_url
        return HttpResponseRedirect(success_url)


    def form_invalid(self, main_form):
        if main_form.errors:
            for field, error in main_form.errors.items():
                
                error_text = f"{''.join(field).join(error)}"
                messages.error(self.request, error_text)

        success_url = self.success_url
        return HttpResponseRedirect(success_url)
    


class AppartmentCreateView(TemplateView):

    model = Appartment
    template_name = 'appartments/appartments_edit.html'
    success_url = reverse_lazy('appartments:appartments_list')
    form_class = AppartmentCreateForm



    def post(self, request, *args, **Kwargs):
        main_form = AppartmentCreateForm(request.POST, prefix='main_form')
        if (main_form.is_valid()):
            return self.form_valid(main_form)
        else: 
            return self.form_invalid(main_form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['main_form'] = AppartmentCreateForm(prefix='main_form')
        return context

    def form_valid(self, main_form):
        main_form.save()
        messages.success(self.request, 'Квартира создана')
        success_url = self.success_url
        return HttpResponseRedirect(success_url)


    def form_invalid(self, main_form):
        if main_form.errors:
            for field, error in main_form.errors.items():
                
                error_text = f"{''.join(field).join(error)}"
                messages.error(self.request, error_text)

        success_url = self.success_url
        return HttpResponseRedirect(success_url)

    # ------------------------------------------------------------------------
    # -------------------PERSONALE-ACCOUNT-CRUD-------------------------------
    # ------------------------------------------------------------------------

class PersonalAccountsListView(TemplateView):
    template_name = 'appartments/personal_accounts_list.html'

    def get(self, request, *args, **kwargs):

       # datatables serverside logic
        if self.request.is_ajax() and self.request.method == 'GET' and request.GET.get('draw'):
            account_data_get_request = request.GET

            #search logic 
            Q_list = []

            if request.GET.get('columns[0][search][value]'):
                print('----------------------ACCOUNT-NUMBER-FILTER---------------------')
                Q_list.append(Q(number__icontains=request.GET.get('columns[0][search][value]')))


            if request.GET.get('columns[1][search][value]'):
                print('----------------------------STATUS-FILTER------------------------')
                print(request.GET.get('columns[1][search][value]'))
                if request.GET.get('columns[1][search][value]') != 'all_status':
                    Q_list.append(Q(status__icontains=request.GET.get('columns[1][search][value]')))


            if request.GET.get('columns[2][search][value]'):
                print('---------------------APPARTMENT-NUMBER-FILTER---------------------')
                Q_list.append(Q(appartment_account__number__icontains=request.GET.get('columns[2][search][value]')))


            if request.GET.get('columns[3][search][value]'):
                print('----------------------------HOUSE-FILTER------------------------')
                if request.GET.get('columns[3][search][value]') != 'all_houses':
                    chooset_house = House.objects.get(id=request.GET.get('columns[3][search][value]'))
                    Q_list.append(Q(appartment_account__house=chooset_house))
                

            if request.GET.get('columns[4][search][value]'):
                print('----------------------------SECTION-FILTER------------------------')
                if request.GET.get('columns[4][search][value]') != 'empty_sect':
                    print('-----------------TEST_DATA--------------------------------------------')
                    choosed_section = Section.objects.get(id=request.GET.get('columns[4][search][value]'))

                    Q_list.append(Q(appartment_account__sections__title=choosed_section.title))

            if request.GET.get('columns[5][search][value]'):
                print('----------------------------OWNERS-FILTER------------------------')               
                if request.GET.get('columns[5][search][value]'):
                    print(request.GET.get('columns[5][search][value]'))
                    user = User.objects.get(id=request.GET.get('columns[5][search][value]'))
                    Q_list.append(Q(appartment_account__owner_user__full_name=user))


            if request.GET.get('columns[6][search][value]'):
                print('-----------------BALANCE-FILTER-----------------------------')
                print(request.GET.get('columns[6][search][value]'))
                if request.GET.get('columns[6][search][value]') == 'debt':
                    Q_list.append(Q(balance__lt=0))
                elif request.GET.get('columns[6][search][value]') == 'no_debt':
                    Q_list.append(Q(balance__gte=0))
                elif request.GET.get('columns[6][search][value]') == 'all_balance':
                    pass


            draw = int(account_data_get_request.get("draw"))
            start = int(account_data_get_request.get("start"))
            length = int(account_data_get_request.get("length"))

            raw_data = PersonalAccount.objects.filter(*Q_list)\
                                .only('number','status', 'appartment_account__number',\
                                       'appartment_account__house__title', 'appartment_account__sections__title',\
                                          'appartment_account__owner_user__full_name', 'balance')\
                                .order_by('-id')\
                                .values('number','status', 'appartment_account__number',\
                                         'appartment_account__house__title', 'appartment_account__sections__title',\
                                              'appartment_account__owner_user__full_name', 'balance', 'id')

            data = list(raw_data)
            verbose_status_dict = PersonalAccount.get_verbose_status_dict()


            for account in data:
                verbose_status = ""
                try: 
                    verbose_status = verbose_status_dict[account['status']]
                    account['status'] = verbose_status
                except:
                    account['status'] = ''

                


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

        # datatable serverside sending sections for house changing
        if self.request.is_ajax() and self.request.method == 'GET' and request.GET.get('choosen_house'):
            choosen_house = House.objects.get(title=request.GET.get('choosen_house'))
            sections = list(Section.objects.only('id', 'title').filter(house=choosen_house).values('id', 'title'))
            response = {'sections': sections}
            return JsonResponse(response, safe=False)

        # users search using Select2
        if self.request.is_ajax() and self.request.GET.get('issue_marker') == 'all_owners':
            owners_data = list(User.objects.filter(owning__isnull=False).values('id', 'full_name'))
            for owner_dict in owners_data: owner_dict['text'] = owner_dict.pop('full_name')
            data = {'results': owners_data}
            return JsonResponse(data)

        # test code for ajax_requests
        if self.request.is_ajax() and self.request.GET.get('issue_marker') == 'owners':
            if self.request.GET.get('search'):
                search_data = self.request.GET.get('search')
                owners_data = list(User.objects.filter(Q(owning__isnull=False) & Q(full_name__icontains=search_data)).values('id', 'full_name'))
                for owner_dict in owners_data: owner_dict['text'] = owner_dict.pop('full_name')
                data = {'results': owners_data}
                return JsonResponse(data)

        else:
            context = self.get_context_data(**kwargs)
            return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['general_statistics'] = GraphTotalStatistic.objects.first()
        context['houses'] = House.objects.all()
        return context
    # ---------------------------------------------------------------------------------------------------------------------------------------------
class PersonalAccountAddView(TemplateView):
    template_name = 'appartments/personal_accounts_create.html'    
    form_class = PersonalAccountCreateForm
    model = PersonalAccount
    success_url = reverse_lazy('appartments:personal_accounts_list')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['main_form'] = PersonalAccountCreateForm(prefix='main_form') 
        return context

    def get(self, request, *args, **kwargs):
        
        if self.request.is_ajax() and self.request.method == 'GET' and self.request.GET.get('ajax_indicator') == 'get_initial_appartment_data':
            appartment_id = self.request.GET['current_appartment_number']
            current_appartment = Appartment.objects.get(id=appartment_id)
            choosen_house = current_appartment.house
            choosen_section = current_appartment.sections
            sections = list(Section.objects.filter(house=choosen_house).values('id'))
            appartment = list(Appartment.objects.filter(sections=choosen_section).values('id'))
            response = {'sections': sections, 'appartment': appartment}
            return JsonResponse(response, safe=False)

        if self.request.is_ajax() and self.request.method == 'GET' and self.request.GET.get('ajax_indicator') == 'get_certain_house':
            house_id = self.request.GET['current_house_number']
            house = House.objects.get(id=house_id)
            # print(house)
            sections = list(Section.objects.only('id', 'title').filter(house=house).values('id', 'title'))
            q_list = []
            q_list.append(Q(house=house))
            q_list.append(Q(Q(personal_account__isnull=True)))
            appartments = list(Appartment.objects.filter(*q_list).values('id', 'number'))
            # print(appartments)
            response = {'sections': sections,
                        'appartments':appartments}
            return JsonResponse(response, safe=False)

        if self.request.is_ajax() and self.request.method == 'GET' and self.request.GET.get('ajax_indicator') == 'get_appartments_per_sections':
            sections_id = self.request.GET.get('current_sections_number')
            choosen_sections = Section.objects.get(id=sections_id)
            q_list = []
            q_list.append(Q(sections__id=choosen_sections.id))
            q_list.append(Q(personal_account__isnull=True))
            appartments = list(Appartment.objects.filter(*q_list).values('id', 'number'))
            response = {'appartments':appartments}
            return JsonResponse(response, safe=False)

        if self.request.is_ajax() and self.request.method == 'GET' and self.request.GET.get('ajax_indicator') == 'get_owner_and_phone_per_appartment':
            appartment_id = self.request.GET.get('current_appartment_id')
            owner_data = list(Appartment.objects.filter(id=appartment_id).values('owner_user__id', 'owner_user__full_name', 'owner_user__phone'))
            
            response = {}

            if owner_data[0]['owner_user__id']:
                response['user_id'] = owner_data[0]['owner_user__id']

            if owner_data[0]['owner_user__full_name']:
                response['user_full_name'] = owner_data[0]['owner_user__full_name']
            else:
                response['user_full_name'] = "Не указан"

            if owner_data[0]['owner_user__phone']:
                response['user_phone'] = owner_data[0]['owner_user__phone']
            else:
                response['user_phone'] = "Не указан"

            return JsonResponse(response, safe=False)


        else:
            return super().get(request, *args, **kwargs)


    def post(self, request, *args, **Kwargs):
        main_form = PersonalAccountCreateForm(request.POST, prefix='main_form')        
        if main_form.is_valid():
            return self.form_valid(main_form)
        else:
            if main_form.errors:
                for field, error in main_form.errors.items():
                    print(f'{field}: {error}')

    def form_valid(self, main_form):
        main_form.save()
        success_url = self.success_url
        messages.success(self.request, f"Лицевой счет создан!!")
        return HttpResponseRedirect(success_url)
    

class PersonalAccountEditeView(UpdateView):
    template_name = 'appartments/personal_accounts_create.html'
    form_class = PersonalAccountCreateForm
    model = PersonalAccount
    success_url = reverse_lazy('appartments:personal_accounts_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['main_form'] = PersonalAccountCreateForm(instance=self.get_object(), prefix='main_form')
        return context
    
    def post(self, request, *args, **Kwargs):
        main_form = PersonalAccountCreateForm(request.POST, instance=self.get_object(), prefix='main_form')
        if main_form.is_valid():
            return self.form_valid(main_form)
        else:
            if main_form.errors:
                for field, error in main_form.errors.items():
                    print(f'{field}: {error}')

    def form_valid(self, main_form):
        main_form.save()
        success_url = self.success_url
        messages.success(self.request, f"Изменения в лицевой счет внесены!")
        return HttpResponseRedirect(success_url)
    


class PersonalAccountDeleteView(DeleteView):
    model = PersonalAccount
    success_url = reverse_lazy('appartments:personal_accounts_list')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        personal_account_number = self.object.number
        personal_account_sum = self.object.balance
        success_url = self.get_success_url()
        general_statistics = GraphTotalStatistic.objects.first()
        if personal_account_sum < 0:
            general_statistics.total_debt -= personal_account_sum
        general_statistics.total_balance -= personal_account_sum
        self.object.delete()

        messages.success(request, (f"Лицевой счет '{personal_account_number}' удален."))
        return HttpResponseRedirect(success_url)


    # ------------------------------------------------------------------------
    # -------------------APPARTMENT-OWNERS-CRUD-------------------------------
    # ------------------------------------------------------------------------
class OwnersListView(TemplateView):
    template_name = 'appartments/owner_list.html'

    def get(self, request, *args, **kwargs):

       # datatables serverside logic
        if self.request.is_ajax() and self.request.method == 'GET' and request.GET.get('draw'):
            account_data_get_request = request.GET

            #search logic 
            Q_list = []
            Q_list.append(Q(owning__isnull=False))

            # id filtering
            if request.GET.get('columns[0][search][value]'):
                Q_list.append(Q(id__icontains=request.GET.get('columns[0][search][value]')))

            # full name filtering
            if self.request.is_ajax() and request.GET.get('columns[1][search][value]'):
                    search_full_name_list_parameter = list((request.GET.get('columns[1][search][value]').strip()).split(" "))
                    Q_list.append(reduce(operator.and_, (Q(full_name__icontains=part_name) for part_name in search_full_name_list_parameter)))
                
            # phone filtering
            if request.GET.get('columns[2][search][value]'):
                if request.GET.get('columns[2][search][value]') != 'all_phones':
                    Q_list.append(Q(phone__icontains=request.GET.get('columns[2][search][value]')))

            # email filtering
            if request.GET.get('columns[3][search][value]'):
                if request.GET.get('columns[3][search][value]') != 'all_phones':
                    Q_list.append(Q(email__icontains=request.GET.get('columns[3][search][value]')))

            if request.GET.get('columns[4][search][value]'):
                if request.GET.get('columns[4][search][value]') != 'all_houses':
                    Q_list.append(Q(owning__house=request.GET.get('columns[4][search][value]')))


            # appartment filtering
            if self.request.is_ajax() and request.GET.get('columns[5][search][value]'):
                    search_apartment_list_parameter = list((request.GET.get('columns[5][search][value]').strip()).split(" "))
                    Q_list.append(reduce(operator.and_, (Q(appartments_in_owning__icontains=part_addr) for part_addr in search_apartment_list_parameter)))

            # users creating
            if request.GET.get('columns[6][search][value]'):
                date_list = request.GET.get('columns[6][search][value]').split('.')
                date_list.reverse()
                date_string = ''
                date_string = '-'.join(str(elem) for elem in date_list)
                formated_date = datetime.strptime(date_string, '%Y-%m-%d')
                Q_list.append(Q(created_at=formated_date))


            # status filter
            if request.GET.get('columns[7][search][value]'):
                if request.GET.get('columns[7][search][value]') != 'all_status':
                    Q_list.append(Q(status=request.GET.get('columns[7][search][value]')))

            # debt filter
            if request.GET.get('columns[8][search][value]'):
                if request.GET.get('columns[8][search][value]') == 'debt':
                    Q_list.append(Q(owning__personal_account__balance__lt=0))


            draw = int(account_data_get_request.get("draw"))
            start = int(account_data_get_request.get("start"))
            length = int(account_data_get_request.get("length"))

            
            raw_data = User.objects.annotate(appartments_in_owning = ArrayAgg(Concat(Value('['),
                                                                                    F('owning__id'),
                                                                                    Value(']-['),
                                                                                    F('owning__house__title'),
                                                                                    Value(']-['),
                                                                                    F('owning__number'),
                                                                                    Value(']'),
                                                                                    output_field=CharField())
                                                                                    ,distinct=True))\
                                    .annotate(house_in_owning = ArrayAgg('owning__house__title', distinct=True))\
                                    .annotate(current_balance = Sum('owning__personal_account__balance', distinct=True))\
                                    .filter(*Q_list)\
                                    .order_by()\
                                    .values('id','full_name', 'phone',\
                                            'email', 'house_in_owning',\
                                            'appartments_in_owning', 'created_at',\
                                            'status', 'current_balance')

            data = list(raw_data)
            # print(data)
            verbose_status_dict = User.get_verbose_status_dict()

            for owner in data:  
                verbose_status = ""
                try: 
                    verbose_status = verbose_status_dict[owner['status']]
                    owner['status'] = verbose_status
                except:
                    owner['status'] = ''


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
        context['houses'] = House.objects.all()
        return context



# from django.shortcuts import redirect
# class OwnerSendInvitation(FormView):
# def send_owner_invitaion(request):
#     if request.method == "POST":
#         send_form = SendOwnderForm(request.POST)
#         if send_form.is_valid():
#             send_form.send()
#             messages.success(request, f'Приглашение отправлено!')
#             return redirect('appartment:owner_list')
#         else:
#             send_form = SendOwnderForm()



class OwnerSendInvitation(FormView):
    form_class = SendOwnderForm
    template_name = "appartments/owner_send_invitation.html"

    def form_valid(self, send_form):
        send_form.send()
        messages.success(self.request, (f"Приглашение отправлено!"))
        response = HttpResponseRedirect(reverse_lazy('appartments:owner_list'))
        return response

    def post(self, request, *args, **Kwargs):
        send_form = SendOwnderForm(request.POST)
        if send_form.is_valid():
            return self.form_valid(send_form)
        else:
            if send_form.errors:
                for field, error in send_form.errors.items():
                    print(f'{field}: {error}')



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)     
        context['send_form'] = SendOwnderForm()
        return context




from receipts.services import return_xlm_statement_data
def personal_accounts_print_all(request):
    response = return_xlm_statement_data()
    return response

class OwnerCardView(DetailView):
    queryset = User.objects.all()    
    template_name = "appartments/owner_card.html"
    context_object_name = 'owner'



class OwnerEditeView(UpdateView):
    form_class = OwnerUpdateForm
    model = User
    template_name = 'appartments/owner_update.html'
    success_url = reverse_lazy('appartments:owners_list')


class OwnerDeleteView(DeleteView):

    model = User
    success_url = reverse_lazy('appartments:owners_list')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        owner_email = self.object.email
        success_url = self.get_success_url()
        self.object.delete()
        messages.success(request, (f"Собственник квартиры с электронной почтой '{owner_email}'. Удален."))
        return HttpResponseRedirect(success_url)
    

class CreteNewUser(CreateView):

    template_name = 'appartments/owner_create.html'
    form_class = OwnerUpdateForm
    success_url = reverse_lazy('appartments:owners_list')


    def form_invalid(self, form):
        if form.errors:
            for field, error in form.errors.items():
                error_text = f"{''.join(error)}"
                messages.error(self.request, error_text)
        return self.render_to_response(self.get_context_data(form=form))


