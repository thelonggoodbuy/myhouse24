import math
import operator
from functools import reduce
from babel.dates import format_date, format_datetime

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


from datetime import date, datetime
import html2text
import calendar




from .forms import LoginSimpleUserForm, LoginAdminUserForm, SignUpSimpleUserForm, AdminSettingsUsersUpdateForm,\
                    UsersRolesFormSet, AdminSettingsUsersRolesCellForm, MessageToUserForm





class LoginSimpleUser(SuccessMessageMixin, LoginView):
    template_name = 'users/login_user.html'
    form_class = LoginSimpleUserForm

    def get_success_url(self):
        return reverse_lazy('appartments:report_view')

    def form_invalid(self, form):
        messages.error(self.request,'Ошибка в адресе электронной почты или в пароле')
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_message(self, cleaned_data):
        return f"Добро пожаловать, {self.request.user.email}"

    def form_valid(self, form):
        remember_me = form.cleaned_data['remember_me']
        # if not remember_me:
        #     self.request.session.set_expiry(0) 
        #     self.request.session.modified = True
        #     print(self.request.session.get_expiry_age())
        return super(LoginSimpleUser, self).form_valid(form)


class LoginAdminUser(SuccessMessageMixin, LoginView):
    template_name = 'users/login_admin.html'
    form_class = LoginAdminUserForm

    def get_success_url(self):
        return reverse_lazy('receipts:crm_report_view')

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

class AdminSettingsUsersListLogic(TemplateView):
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


class AdminSettingsUserCardView(DetailView):

    queryset = User.objects.select_related('role').only('name', 'surname', 'role__name', 'phone', 'email', 'status')
    template_name = "users/admin_settings_user_card.html"
    context_object_name = 'user'


class AdminSettingsUsersDeleteView(DeleteView):

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
    

class AdmSettingsUsersUpdateView(UpdateView):
    form_class = AdminSettingsUsersUpdateForm
    model = User
    template_name = 'users/admin_settings_user_update_data.html'
    success_url = reverse_lazy('users:admin_settings_users_list')


class AdminSettingsUsersRolesView(FormView):
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


class AppartmentsOwnersView(RolePassesTestMixin, TemplateView):
    template_name = "users/appartments_owners.html"
    needfull_permission = 'owners_permission'
    needfull_user_status = 'is_staff'


class PermissionDeniedView(TemplateView):
    template_name = "users/permission_denied.html"


# messages logic
class MessagesListView(TemplateView):
    
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
    


class MessageCreateView(CreateView):

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
    


class MessageDetailView(DetailView):
    model = MessageToUser
    template_name = "users/message_detail.html"
    context_object_name = 'message'


class MessageDeleteView(DeleteView):
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
    
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

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

        # print('=========================================================')
        # print(all_receipts_list)
        # print('=========================================================')

        context['average_consumption_per_month'] = (summ_consumption)/12

        # prev_month = ((date.today().replace(day=1) - timedelta(days=1)).month)
        
        # first_date_prev_month = date(date.today().month, prev_month, 1)
        # first_date_prev_month = (date(date.today().month, prev_month, 1)).strftime("%Y-%m-%d")

        # next_month = date.today().month + 1


        # last_date_this_month = date(date.today().month, 12, 31)

        # print(prev_month)
        # print('=========================================================')
        # # print(next_month)
        # print(date.today().month) 
        # print('=========================================================')

        # all_receipts_cells = ReceiptCell.objects.filter().values(Q(receipt__from_date__gt=first_date)\
        #                                                         and Q(receipt__from_date__lt=last_date)\
        #                                                         and Q(receipt__appartment=self.object))

        first_day_previous_month = ((datetime.today() - relativedelta(months=1)).replace(day=1)).date()
        last_day_previous_month = ((datetime.today().replace(day=1)) - relativedelta(days=1)).date()
        


        all_receipts_cells = list(ReceiptCell.objects.filter(Q(receipt__from_date__gt=first_date)\
                                                                and Q(receipt__from_date__lt=last_date)\
                                                                and Q(receipt__appartment=self.object))\
                                                        .values('utility_service__title', 'cost', 'receipt__from_date'))
                                                                
        
        for receipt_cell in all_receipts_cells: receipt_cell['month'] = receipt_cell['receipt__from_date'].strftime("%B")


        # print(all_receipts_cells)

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




        # print((list(calendar.month_name))[1:])


        context['all_month_per_utility'] = all_month_per_utility
        context['previous_month_per_utility'] = previous_month_per_utility
        context['all_month_summ'] = all_month_summ

        # print(context)

        return context