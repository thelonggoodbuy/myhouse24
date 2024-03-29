import math
import operator
from functools import reduce
from babel.dates import format_date, format_datetime


from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from django.shortcuts import render, redirect
# from django.views.generic import LoginView
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.edit import CreateView
from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy
from django.contrib import messages
from datetime import timedelta
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.views.generic.base import View, TemplateView
from django.http import  JsonResponse

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models.functions import Concat
from django.db.models import F, Q, CharField, Value, Case, When


from receipts.models import Receipt, ReceiptCell
from .tokens import account_activation_token
from .models import User, Role, MessageToUser
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView, UpdateView, FormView
from django.views.generic.detail import SingleObjectTemplateResponseMixin
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.list import ListView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from appartments.models import House, Section, Floor, Appartment
from utility_services.models import TariffCell
from masters_services.models import MastersRequest
# from users.views import RolePassesTestMixin


from datetime import date, datetime
import html2text
import calendar




from .forms import LoginSimpleUserForm, LoginAdminUserForm, SignUpSimpleUserForm, AdminSettingsUsersUpdateForm,\
                    UsersRolesFormSet, AdminSettingsUsersRolesCellForm, MessageToUserForm, ProfileMastersRequestsCreateForm


class RolePassesTestMixin(UserPassesTestMixin, LoginRequiredMixin):

    def test_func(self):
        # try to get needfull_user_status class field
        if hasattr(self.__class__, 'needfull_user_status'):
            needfull_user_status = self.__class__.needfull_user_status
            if getattr(self.request.user, needfull_user_status) == False:
                self.permission_denied_message = 'Вы не обладаете нужным статусом пользователя'
                return False


        # try to get needfull_permission class field
        if hasattr(self.__class__, 'needfull_permission'):
            needfull_permission = self.__class__.needfull_permission
            try:
                this_role_perm = self.request.user.role.return_permission_is(needfull_permission)
                if this_role_perm == True:
                    return True
                else:
                    self.permission_denied_message = "У вашей роли нет права работать с этими данными"
                    return False
            except AttributeError:
                return False


    def handle_no_permission(self):
        error_text = self.get_permission_denied_message()
        messages.error(self.request, error_text)
        return redirect('users:permission_denied')




class LoginSimpleUser(SuccessMessageMixin, LoginView):
    template_name = 'users/login_user.html'
    form_class = LoginSimpleUserForm

    def get_success_url(self):
        # return reverse_lazy('users:profile_user_detail')
        return reverse_lazy('users:profile_user_detail', kwargs={'pk': self.request.user.id})

    def form_invalid(self, form):
        messages.error(self.request,'Ошибка в адресе электронной почты или в пароле')
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_message(self, cleaned_data):
        return f"Добро пожаловать, {self.request.user.email}"

    def form_valid(self, form):
        return super(LoginSimpleUser, self).form_valid(form)


class LoginAdminUser(SuccessMessageMixin, LoginView):
    template_name = 'users/login_admin.html'
    form_class = LoginAdminUserForm

    def get_success_url(self):
        return reverse_lazy('appartments:appartments_list')

    def form_invalid(self, form):
        messages.error(self.request,'Ошибка в адресе электронной почты или в пароле')
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_message(self, cleaned_data):
        return f"Добро пожаловать, {self.request.user.email}"

    def form_valid(self, form):
        return super(LoginAdminUser, self).form_valid(form)


# class SignUpSimpleUser(SuccessMessageMixin, CreateView):
class SignUpSimpleUser(CreateView):

    template_name = 'users/sign_up_simple_user.html'
    form_class = SignUpSimpleUserForm


    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()

        current_site = get_current_site(self.request)
        subject = 'Activate You MySite Account'
        message = render_to_string('email_templates/account_activation_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        })
        # ******тут отправляю. можно добавить ссылку туда**********
        user.email_user(subject, message)
        print('Ваш профиль зарегистрирован, но не активирован. Пожалуйста подтвердите регистрацию через письмо полученное на почту.')
        messages.info(self.request, ('Ваш профиль зарегистрирован, но не активирован. Пожалуйста подтвердите регистрацию через письмо полученное на почту.'))
        return super(SignUpSimpleUser, self).form_valid(form)


    def form_invalid(self, form):
        if form.errors:
            for field, error in form.errors.items():
                error_text = f"{''.join(error)}"
                messages.error(self.request, error_text)
        return self.render_to_response(self.get_context_data(form=form))



class ActivateAccount(View):
    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.profile.email_confirmed = True
            user.save()
            login(request, user)
            messages.success(request, ('Ваш профиль активирован.'))
            return redirect('users:login_user')
        else:
            messages.warning(request, ('Ссылка активации не активна. ВОзможно Вы воспользовались ею раньше'))
            return redirect('users:login_user')



class SignUpAdminUser(SuccessMessageMixin, CreateView):
    pass


class LogOutUser(LogoutView):

    def get_success_url(self):
        return reverse_lazy('users:login_user')



# ***************************************************************************************
# *******************************Settings---->Users Logic********************************
# ***************************************************************************************

class AdminSettingsUsersListLogic(RolePassesTestMixin, TemplateView):
    needfull_permission = 'users_sections_permission'
    needfull_user_status = 'is_staff'
    template_name = "users/admin_settings_users_list.html"

    def get(self, request, *args, **kwargs):
        
        if self.request.is_ajax() and self.request.method == 'GET':
            # server-side processing - columns search parameters
            Q_list = []
            data_table_request = request.GET
            search_full_name_list_parameter = list((request.GET.get('columns[1][search][value]').strip()).split(" "))

            Q_list.append(reduce(operator.and_, (Q(full_name__icontains=part_name) for part_name in search_full_name_list_parameter)))

            if request.GET.get('columns[2][search][value]'):
                Q_list.append(Q(role__name__icontains=request.GET.get('columns[2][search][value]')))

            if request.GET.get('columns[3][search][value]'):
                Q_list.append(Q(phone__icontains=request.GET.get('columns[3][search][value]')))

            if request.GET.get('columns[4][search][value]'):
                Q_list.append(Q(email__icontains=request.GET.get('columns[4][search][value]')))

            if request.GET.get('columns[5][search][value]'):
                Q_list.append(Q(status__icontains=request.GET.get('columns[5][search][value]')))


            # initial data
            draw = int(data_table_request.get("draw"))
            start = int(data_table_request.get("start"))
            length = int(data_table_request.get("length"))

            # server-side processing - db handling
            raw_data = User.objects.select_related('role').filter(*Q_list)\
                                    .only('id','name', 'surname', 'patronymic', 'phone', 'role__name', 'email', 'status', 'is_superuser')\
                                    .order_by('id')\
                                    .values('id','name', 'surname', 'patronymic', 'phone', 'role__name', 'email', 'status', 'is_superuser')
                        
            data = list(raw_data)
            verbose_status_dict = User.get_verbose_status_dict()
            # verbose_roles_dict = User.get_verbose_roles_dict()

            for user in data:
                user['full_name'] = f"{user['name']} {user['surname']} {user['patronymic']}"

                verbose_status = ""
                try: 
                    verbose_status = verbose_status_dict[user['status']]
                    user['verbose_status'] = verbose_status
                except:
                    user['verbose_status'] = ''

            paginator = Paginator(data, length)
            page_number = start / length + 1
            try:
                obj = paginator.page(page_number).object_list
            except PageNotAnInteger:
                obj = paginator.page(1).object_list
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
            # print(response)
            return JsonResponse(response, safe=False)
        else:
            context = self.get_context_data(**kwargs)
            return self.render_to_response(context)



    def post(self, request, *args, **kwargs):
        if self.request.is_ajax() and self.request.method == 'POST':
            user_id = request.POST.get("data", None)
            print(f'you use AJAX Post method. Congradulations! User number is {user_id}')
            # User.objects.get(id = user_id).delete()
            uri = request.build_absolute_uri(reverse('users:admin_settings_users_card', args=(user_id, )))
            print(uri)
            return JsonResponse({'uri': uri})

        else:
            context = self.get_context_data(**kwargs)
            return self.render_to_response(context)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class AdminSettingsUserCardView(RolePassesTestMixin, DetailView):
    needfull_permission = 'users_sections_permission'
    needfull_user_status = 'is_staff'
    queryset = User.objects.select_related('role').only('name', 'surname', 'role__name', 'phone', 'email', 'status')
    template_name = "users/admin_settings_user_card.html"
    context_object_name = 'user_object'


class AdminSettingsUsersDeleteView(RolePassesTestMixin, DeleteView):
    needfull_permission = 'users_sections_permission'
    needfull_user_status = 'is_staff'
    model = User
    success_url = reverse_lazy('users:admin_settings_users_list')
    

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        user_id = self.object.id
        success_url = self.get_success_url()
        self.object.delete()
        messages.success(request, (f'Пользователь с id {user_id}. Удален.'))
        return HttpResponseRedirect(success_url)
    

class AdmSettingsUsersUpdateView(RolePassesTestMixin, UpdateView):
    needfull_permission = 'users_sections_permission'
    needfull_user_status = 'is_staff'
    form_class = AdminSettingsUsersUpdateForm
    model = User
    template_name = 'users/admin_settings_user_update_data.html'
    success_url = reverse_lazy('users:admin_settings_users_list')


class AdminSettingsUsersRolesView(RolePassesTestMixin, FormView):
    needfull_permission = 'role_section_permission'
    needfull_user_status = 'is_staff'
    model = Role
    template_name = "users/admin_settings_users_roles.html"
    success_url = reverse_lazy('users:adm_settings_users_roles')
    
    form_class = AdminSettingsUsersRolesCellForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['roles_formset'] = UsersRolesFormSet(queryset=Role.objects.all())
        return context
    
    def post(self, request, *args, **Kwargs):
        current_formset = UsersRolesFormSet(request.POST)
        if current_formset.is_valid():
            return self.form_valid(current_formset)
        else:
            print(current_formset.errors)
        
    def form_valid(self, current_formset):
        current_formset.save()
        return super(AdminSettingsUsersRolesView, self).form_valid(current_formset)
    



# -----------------------------------------------------------------------------------------
# -----------------------------Appartments Owner-------------------------------------------
# -----------------------------------------------------------------------------------------


class AppartmentsOwnersView(RolePassesTestMixin, TemplateView):
    template_name = "users/appartments_owners.html"
    needfull_permission = 'owners_permission'
    needfull_user_status = 'is_staff'


class PermissionDeniedView(TemplateView):
    template_name = "users/permission_denied.html"


# messages logic
class MessagesListView(RolePassesTestMixin, TemplateView):
    needfull_permission = 'messages_permission'
    needfull_user_status = 'is_staff'
    template_name = 'users/messages_list.html'

    def get(self, request, *args, **kwargs):
        
       # datatables serverside logic
        if self.request.is_ajax() and self.request.method == 'GET' and request.GET.get('draw'):
            Q_list = []
            account_data_get_request = request.GET

            if request.GET.get('search[value]'):
                Q_list.append(Q(topic__icontains=request.GET.get('search[value]')))


            #search logic
            draw = int(account_data_get_request.get("draw"))
            start = int(account_data_get_request.get("start"))
            length = int(account_data_get_request.get("length"))

            raw_data = MessageToUser.objects.annotate(
                                                text_with_title = Case(
                                                    When(message_target_type='one_user', then=F('to_users__full_name')),
                                                    When(message_target_type='all_users_per_house', then=(F('to_users__owning__house__title'))),
                                                    # ------------------------------------------------------------------------------------
                                                    When(message_target_type='all_users_per_floor', then=(Concat(
                                                                                                    F('to_users__owning__house__title'),
                                                                                                    Value(', '),
                                                                                                    F('to_users__owning__floor__title'),
                                                                                                    output_field=CharField()
                                                                                                    ))),
                                                    When(message_target_type='all_users_per_sections', then=(Concat(
                                                                                                    F('to_users__owning__house__title'),
                                                                                                    Value(', '),
                                                                                                    F('to_users__owning__sections__title'),
                                                                                                    output_field=CharField(),
                                                                                                    distinct=True
                                                                                                    ))),
                                                    When(message_target_type='all_users', then=Value('все')),
                                                    distinct=True,
                                                    output_field=CharField()
                                                    ))\
                                            .filter(*Q_list)\
                                            .only('text_with_title', 'topic','text', 'date_time','id')\
                                            .order_by('-id')\
                                            .values('text_with_title', 'topic', 'text', 'date_time', 'id')


            data = list({v['id']: v for v in list(raw_data)}.values())

            for message in data:  
                date_time = message['date_time']
                formated_date_time = format_datetime(date_time, 'dd.MM.yyyy - HH:mm', locale='ru')
                message['date_time'] = formated_date_time

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
        

    def post(self, request, **kwargs):
        if request.POST.get('ajax_indicator') == 'delete_request':
            test_list = request.POST.getlist('delete_list[]')
            # print(test_list)
            delete_set = MessageToUser.objects.filter(pk__in=test_list)
            delete_set.delete()
            # messages.success(self.request,'Вы удалили сообщения')
            response = 'You finished deleteting!'
            return JsonResponse(response, safe=False)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    


class MessageCreateView(RolePassesTestMixin, CreateView):
    needfull_permission = 'messages_permission'
    needfull_user_status = 'is_staff'
    template_name = 'users/message_create.html'
    form_class = MessageToUserForm
    success_url = reverse_lazy('users:message_list_view')


    def get(self, request, *args, **kwargs):

        if self.request.is_ajax() and self.request.method == 'GET' and self.request.GET.get('ajax_indicator') == 'get_certain_house':
            house_id = self.request.GET['current_house_number']
            house = House.objects.get(id=house_id)
            sections = list(Section.objects.only('id', 'title').filter(house=house).values('id', 'title'))
            floors = list(Floor.objects.only('id', 'title').filter(house=house).values('id', 'title'))
            appartments = list(Appartment.objects.only('id', 'number').filter(house=house).values('id', 'number'))
            response = {'sections': sections,
                        'appartments':appartments,
                        'floors': floors}
            return JsonResponse(response, safe=False)
        

        if self.request.is_ajax() and self.request.method == 'GET' and self.request.GET.get('ajax_indicator') == 'get_appartments_per_sections':
            sections_id = self.request.GET['current_sections_number']
            sections = Section.objects.get(id=sections_id)
            appartments = list(Appartment.objects.only('id', 'number').filter(sections=sections).values('id', 'number'))
            response = {'appartments':appartments}
            return JsonResponse(response, safe=False)
        

        if self.request.is_ajax() and self.request.method == 'GET' and self.request.GET.get('ajax_indicator') == 'get_appartments_per_floor':
            floor_id = self.request.GET['current_floor_number']
            floor = Floor.objects.get(id=floor_id)
            appartments = list(Appartment.objects.only('id', 'number').filter(floor=floor).values('id', 'number'))
            response = {'appartments':appartments}
            return JsonResponse(response, safe=False)

        else:
            return super().get(request, *args, **kwargs)



    def post(self, request, *args, **Kwargs):
        message_form = MessageToUserForm(request.POST, prefix="message_to_user")

        if message_form.is_valid():
            return self.form_valid(message_form)
        else:
            if message_form.errors:
                for field, error in message_form.errors.items():
                    print(f'{field}: {error}')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # print(self.request.user)
        # print(self.request.user.id)
        context['message_form'] = MessageToUserForm(prefix="message_to_user")
        return context
    
    def form_valid(self, message_form):
        message = message_form.save(commit=False)
        message.from_user = self.request.user
        message_form.save()
        return HttpResponseRedirect(self.success_url)
    


class MessageDetailView(RolePassesTestMixin, DetailView):
    needfull_permission = 'messages_permission'
    needfull_user_status = 'is_staff'
    model = MessageToUser
    template_name = "users/message_detail.html"
    context_object_name = 'message'


class MessageDeleteView(RolePassesTestMixin, DeleteView):
    needfull_permission = 'messages_permission'
    needfull_user_status = 'is_staff'
    model = MessageToUser
    success_url = reverse_lazy('users:message_list_view')
    
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        message_topic = self.object.topic
        success_url = self.get_success_url()
        self.object.delete()
        messages.success(request, (f"Сообщение '{message_topic}' удалено."))
        return HttpResponseRedirect(success_url)
    

# ---------------------------------CABINET-LOGIC---------------------------------------------
class ProfileDetailView(DetailView):
    model = User
    template_name = 'users/profile_detail.html'

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj
    

class ProfileStatisticPerAppartment(DetailView):
    model = Appartment
    template_name = 'users/profile_statistic_per_appartment.html'
    context_object_name = 'appartment'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        first_date = date(date.today().year, 1, 1)
        last_date = date(date.today().year, 12, 31)
        
        all_receipts_list = list(Receipt.objects.filter(Q(from_date__gt=first_date) and Q(from_date__lt=last_date) and Q(appartment=self.object))\
                                            .values("from_date", "total_sum",\
                                                     "status", "payment_was_made", "id"))
        
        recieipt_stat_dict = {}
        for month in (list(calendar.month_name))[1:]:
            recieipt_stat_dict[month] = {'total_debd':0, 'total_payed':0}

        for receipt in all_receipts_list:
            receipt_month = receipt['from_date'].strftime("%B")
            recieipt_stat_dict[receipt_month]['total_debd'] += receipt["total_sum"]
            if receipt['payment_was_made'] == True and receipt['status'] == 'paid_for':
                recieipt_stat_dict[receipt_month]['total_payed'] += receipt["total_sum"]
        summ_consumption = 0.0

        for consumption in recieipt_stat_dict.items():
            summ_consumption += float(consumption[1]['total_debd'])

        context['average_consumption_per_month'] = (summ_consumption)/12

        first_day_previous_month = ((datetime.today() - relativedelta(months=1)).replace(day=1)).date()
        last_day_previous_month = ((datetime.today().replace(day=1)) - relativedelta(days=1)).date()
        
        all_receipts_cells = list(ReceiptCell.objects.filter(Q(receipt__from_date__gt=first_date)\
                                                                and Q(receipt__from_date__lt=last_date)\
                                                                and Q(receipt__appartment=self.object))\
                                                        .values('utility_service__title', 'cost', 'receipt__from_date'))
                                                                        
        for receipt_cell in all_receipts_cells: receipt_cell['month'] = receipt_cell['receipt__from_date'].strftime("%B")

        all_month_per_utility = {}
        previous_month_per_utility = {}
        all_month_summ = {}

        for month in (list(calendar.month_name))[1:]: all_month_summ[month] = 0

        for receipt in all_receipts_cells:
            if receipt['utility_service__title'] in all_month_per_utility:
                all_month_per_utility[receipt['utility_service__title']] += receipt['cost']
            else:
                all_month_per_utility[receipt['utility_service__title']] = receipt['cost']
                
                    
            if receipt['utility_service__title'] in previous_month_per_utility:
                if (receipt['receipt__from_date'] > first_day_previous_month or receipt['receipt__from_date'] == first_day_previous_month) and\
                (receipt['receipt__from_date'] < last_day_previous_month or receipt['receipt__from_date'] == last_day_previous_month):\
                previous_month_per_utility[receipt['utility_service__title']] += receipt['cost']
            else:
                if (receipt['receipt__from_date'] > first_day_previous_month or receipt['receipt__from_date'] == first_day_previous_month) and\
                (receipt['receipt__from_date'] < last_day_previous_month or receipt['receipt__from_date'] == last_day_previous_month):\
                previous_month_per_utility[receipt['utility_service__title']] = receipt['cost']


            if receipt['month'] in all_month_summ:
                all_month_summ[receipt['month']] += receipt['cost']
            else:
                all_month_summ[receipt['month']] = receipt['cost']

        context['all_month_per_utility'] = all_month_per_utility
        context['previous_month_per_utility'] = previous_month_per_utility
        context['all_month_summ'] = all_month_summ

        return context





class ProfileReceiptListView(TemplateView):
    template_name = 'users/profile_receipt_list.html'

    def get(self, request, *args, **kwargs):

        if self.request.is_ajax() and self.request.method == 'GET' and request.GET.get('draw'):
        
            receipt_data_get_request = request.GET
            #search logic 
            Q_list = []

            # number filtering
            if request.GET.get('columns[1][search][value]'):
                Q_list.append(Q(number__icontains=request.GET.get('columns[1][search][value]')))

            # date range search
            if request.GET.get('columns[2][search][value]'):
                date = request.GET.get('columns[2][search][value]')
                formated_date = datetime.strptime(date, '%d.%m.%Y')
                Q_list.append(Q(to_date=formated_date))

            # status filtering
            if request.GET.get('columns[3][search][value]'):
                print(request.GET.get('columns[3][search][value]'))
                if request.GET.get('columns[3][search][value]') != 'all_status':
                    Q_list.append(Q(status=request.GET.get('columns[3][search][value]')))

            
            # payment status filter
            if request.GET.get('columns[4][search][value]'):
                if request.GET.get('columns[4][search][value]') != 'all_payment_status':
                    Q_list.append(Q(payment_was_made=request.GET.get('columns[4][search][value]')))



            Q_list.append(Q(appartment__owner_user=request.user))

            draw = int(receipt_data_get_request.get("draw"))
            start = int(receipt_data_get_request.get("start"))
            length = int(receipt_data_get_request.get("length"))

            raw_data = Receipt.objects.filter(*Q_list)\
                                    .order_by()\
                                    .values('number', 'status', 'to_date',\
                                            'total_sum', "id")

            data = list(raw_data)
            verbose_status_dict = Receipt.get_verbose_status_dict()

            for receipt in data:  
                verbose_status = ""
                try: 
                    verbose_status = verbose_status_dict[receipt['status']]
                    receipt['status'] = verbose_status
                except:
                    receipt['status'] = ''
          

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


class ProfileReceiptListPerAppartmentView(DetailView):
    template_name = 'users/profile_receipt_list_per_appartment.html'
    model = Appartment

    def get(self, request, *args, **kwargs):

        if self.request.is_ajax() and self.request.method == 'GET' and request.GET.get('draw'):
            
            receipt_data_get_request = request.GET
            Q_list = []

            Q_list.append(Q(appartment__id=self.get_object().id))


            # number filtering
            if request.GET.get('columns[1][search][value]'):
                Q_list.append(Q(number__icontains=request.GET.get('columns[1][search][value]')))

            # date range search
            if request.GET.get('columns[2][search][value]'):
                date = request.GET.get('columns[2][search][value]')
                formated_date = datetime.strptime(date, '%d.%m.%Y')
                Q_list.append(Q(to_date=formated_date))

            # status filtering
            if request.GET.get('columns[3][search][value]'):
                print(request.GET.get('columns[3][search][value]'))
                if request.GET.get('columns[3][search][value]') != 'all_status':
                    Q_list.append(Q(status=request.GET.get('columns[3][search][value]')))

            
            # payment status filter
            if request.GET.get('columns[4][search][value]'):
                if request.GET.get('columns[4][search][value]') != 'all_payment_status':
                    Q_list.append(Q(payment_was_made=request.GET.get('columns[4][search][value]')))



            Q_list.append(Q(appartment__owner_user=request.user))

            draw = int(receipt_data_get_request.get("draw"))
            start = int(receipt_data_get_request.get("start"))
            length = int(receipt_data_get_request.get("length"))

            raw_data = Receipt.objects.filter(*Q_list)\
                                    .order_by()\
                                    .values('number', 'status', 'to_date',\
                                            'total_sum', "id")

            data = list(raw_data)
            verbose_status_dict = Receipt.get_verbose_status_dict()

            for receipt in data:  
                verbose_status = ""
                try: 
                    verbose_status = verbose_status_dict[receipt['status']]
                    receipt['status'] = verbose_status
                except:
                    receipt['status'] = ''
          

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
            # context = self.get_context_data(**kwargs)
            # return self.render_to_response(context)
            context = super().get(self, request, *args, **kwargs)
            return context


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context



# from receipts.models import ReceiptTemplate
from receipts.services import cabinet_download_pdf_receipt, cabinet_download_pdf_receipt_for_printing
# =================================WORK AREA=========================================

class ProfileReceiptDetailView(DetailView):
    queryset = Receipt.objects.all()
    template_name = "users/profile_receipt_detail.html"
    context_object_name = 'receipt'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(self.object.id)
        context['receipt_cells'] = ReceiptCell.objects.select_related('utility_service', 'unit_of_measure').filter(receipt=self.object)
        return context




def save_pdf_from_cabinet(request, pk):
    return cabinet_download_pdf_receipt(pk)


def return_pdf_from_cabinet_and_print(request, pk):
    print('========!!!==================')
    return cabinet_download_pdf_receipt_for_printing(pk)

# ============================END==WORK=AREA=========================================




class ProfileTariffListView(DetailView):
    template_name = 'users/profile_tariff_cells_list.html'
    model = Appartment



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tariff_cells'] = TariffCell.objects.filter(tariff=self.get_object().tariff)
        print(context)

        return context
    


class ProfileMessageListView(DetailView):
    template_name = 'users/profile_messages_list.html'
    model = User



    def get(self, request, *args, **kwargs):        
       # datatables serverside logic
        if self.request.is_ajax() and self.request.method == 'GET' and request.GET.get('draw'):
            # print('---------------------------------------')
            # print(self.get_object().id)
            Q_list = []
            account_data_get_request = request.GET
            if request.GET.get('search[value]'):
                Q_list.append(Q(topic__icontains=request.GET.get('search[value]')))

            Q_list.append(Q(to_users__id=self.get_object().id))
            #search logic
            draw = int(account_data_get_request.get("draw"))
            start = int(account_data_get_request.get("start"))
            length = int(account_data_get_request.get("length"))

            raw_data = MessageToUser.objects.filter(*Q_list)\
                                            .only('from_user__full_name', 'topic','text', 'date_time','id')\
                                            .order_by('-id')\
                                            .values('from_user__full_name', 'topic', 'text', 'date_time', 'id')


            data = list({v['id']: v for v in list(raw_data)}.values())

            list_of_dict_readed_messages = list(self.get_object().readed_by_user.all().values('id'))
            list_of_read_messages = [dictionary['id'] for dictionary in list_of_dict_readed_messages]

            for message in data:  
                date_time = message['date_time']
                formated_date_time = format_datetime(date_time, 'dd.MM.yyyy - HH:mm', locale='ru')
                message['date_time'] = formated_date_time

                if message['id'] in set(list_of_read_messages):
                    message['had_been_readed'] = True
                else:
                    message['had_been_readed'] = False


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
            context = super().get(self, request, *args, **kwargs)
            return context
        

    def post(self, request, **kwargs):
        if request.POST.get('ajax_indicator') == 'delete_request':
            test_list = request.POST.getlist('delete_list[]')
            delete_set = MessageToUser.objects.filter(pk__in=test_list)
            for message in delete_set:
                if len(message.to_users.all()) == 1:
                    message.delete()
                else:
                    message.to_users.remove(self.get_object())
                    if message.read_by_user: message.read_by_user.remove(self.get_object())
            response = 'You finished deleteting!'
            return JsonResponse(response, safe=False)



class ProfileMessageDetailView(DetailView):
    template_name = 'users/profile_messages_detail.html'
    model = MessageToUser


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if not self.object.read_by_user.all():
            self.object.read_by_user.add(self.request.user)
            self.object.save()

        return context
    

class ProfileMessageDeleteView(SuccessMessageMixin, DeleteView):
    model = MessageToUser
    success_url = None
    success_message = "Сообщение было удалено!"

    def delete(self, request, *args, **kwargs):
        self.success_url = reverse_lazy('users:profile_message_list', kwargs={'pk': self.request.user.id})
        messages.success(self.request, self.success_message)
        self.object = self.get_object()
        to_users_set = self.object.to_users.all()
        if len(to_users_set) == 1:
            self.object.delete()
        else:
            self.object.to_users.remove(self.request.user)
            if self.object.read_by_user: self.object.read_by_user.remove(self.request.user)        
        success_url = self.get_success_url()

        return HttpResponseRedirect(success_url)
    


class ProfileMastersRequestListView(DetailView):
    template_name = 'users/profile_masters_requests_list.html'
    model = User

    def get(self, request, *args, **kwargs):
        
        # datatables serverside logic
        if self.request.is_ajax() and self.request.method == 'GET' and request.GET.get('draw'):
            masters_get_request = request.GET
            Q_list = []
            user_appartment = request.user.owning.all()
            Q_list.append(Q(appartment__in=user_appartment))
            draw = int(masters_get_request.get("draw"))
            start = int(masters_get_request.get("start"))
            length = int(masters_get_request.get("length"))
            raw_data = MastersRequest.objects.annotate(date_and_time = ArrayAgg(Concat(
                                                                                    F('date_work'),
                                                                                    Value(':'),
                                                                                    F('time_work'),
                                                                                    output_field=CharField())
                                                                                    ,distinct=True))\
                                                                .filter(*Q_list)\
                                                                .only('id', 'master_type', 'description',\
                                                                       'status')\
                                                                .order_by('id')\
                                                                .values('id', 'date_and_time', 'master_type', 'description',\
                                                                        'status')

            data = list(raw_data)
            request_dictionary = MastersRequest.get_request_to_dictionary()
            status_deictionary = MastersRequest.get_status_dictionary()

            for cell in data:
        
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
            context = super().get(self, request, *args, **kwargs)
            return context
        


class ProfileMasterRequestDeleteView(SuccessMessageMixin, DeleteView):
    model = MastersRequest
    success_url = None
    success_message = "Запрос к мастеру удален!"

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


    def delete(self, request, *args, **kwargs):

        self.get_object().delete()
        success_url = reverse_lazy('users:profile_masters_request_list_view', kwargs={'pk': self.request.user.id})        
        messages.success(self.request, self.success_message)

        return HttpResponseRedirect(success_url)





class ProfileMastersRequestsCreateView(FormView):
    template_name = "users/profile_masters_requests_create.html"
    form_class = ProfileMastersRequestsCreateForm
    success_url = None


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)     
        context['masters_request_form'] = ProfileMastersRequestsCreateForm(user=self.request.user, prefix="masters_request_form")
        return context
    

    def post(self, request, *args, **Kwargs):
        masters_request_form = ProfileMastersRequestsCreateForm(request.POST, user=self.request.user, prefix="masters_request_form")
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
        success_url = reverse_lazy('users:profile_masters_request_list_view', kwargs={'pk': self.request.user.id})
        return HttpResponseRedirect(success_url)
    



class ProfileUserDetail(TemplateView):
    template_name = 'users/profile_user_detail.html'
    model = User



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)     
        # owning_data = self.request.user.owning.all().objects.select_related('house__address', 'house__title', 'house__number')
        owning_data = Appartment.objects.select_related('house')\
                                        .filter(owner_user=self.request.user)
        context['owning_data'] = owning_data
        print(context)
        return context