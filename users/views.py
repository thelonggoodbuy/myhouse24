import math
import operator
from functools import reduce

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
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
# from django.contrib.auth.models import User

from .tokens import account_activation_token
from .models import User, Role
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView, UpdateView, FormView
from django.views.generic.detail import SingleObjectTemplateResponseMixin
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.list import ListView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin

import html2text



from .forms import LoginSimpleUserForm, LoginAdminUserForm, SignUpSimpleUserForm, AdminSettingsUsersUpdateForm,\
                    UsersRolesFormSet, AdminSettingsUsersRolesCellForm





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
            print(response)
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
