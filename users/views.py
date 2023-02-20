from django.shortcuts import render
# from django.views.generic import LoginView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy
from django.contrib import messages
from datetime import timedelta
from django.contrib.messages.views import SuccessMessageMixin



from .forms import LoginSimpleUserForm, LoginAdminUserForm





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
        # print('this is superuser')
        # if self.request.user.is_superuser == True:
        #     print('this is superuser')
        # remember_me = form.cleaned_data['remember_me']
        # if not remember_me:
        #     self.request.session.set_expiry(0) 
        #     self.request.session.modified = True
        #     print(self.request.session.get_expiry_age())
        return super(LoginAdminUser, self).form_valid(form)


class LogOutUser(LogoutView):

    def get_success_url(self):
        return reverse_lazy('users:login_user')