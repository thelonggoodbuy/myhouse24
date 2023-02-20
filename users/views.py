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
from django.views.generic.base import View

from django.contrib.auth.models import User

from .tokens import account_activation_token
from .models import User
from django.contrib.messages.views import SuccessMessageMixin


import html2text



from .forms import LoginSimpleUserForm, LoginAdminUserForm, SignUpSimpleUserForm





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
        user.save()
        current_site = get_current_site(self.request)
        subject = 'Activate You MySite Account'
        message = render_to_string('email_templates/account_activation_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        })
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