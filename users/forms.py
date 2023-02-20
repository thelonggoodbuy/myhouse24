from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password


from .models import User




class LoginSimpleUserForm(AuthenticationForm):

    username = forms.EmailField(label='Електронная почта',
                                help_text='E-mail или ID',
                                widget=forms.EmailInput(attrs={'class': 'form-control has-feedback',
                                                                'id': 'loginform-username',
                                                                'placeholder':'Email'}))
    password = forms.CharField(label='Пароль',
                                help_text='Пароль',
                                widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                    'placeholder':'пароль'}))

    remember_me = forms.BooleanField(required=False,
                                        label='запомнить меня')

    class Meta:
        model = User
        fields = ("username", "password",)


    def clean_username(self):
        email = self.cleaned_data['username']
        current_user = User.objects.filter(email=email)
        if current_user.exists() and current_user[0].is_superuser == True:
            self.add_error('username', 'Этот профиль принадлежит администратору. Войдите в систему как администратор.')
            messages.error(self.request,'Этот профиль принадлежит администратору. Войдите в систему как администратор.')

        elif current_user.exists() == False:
            self.add_error('username', 'Пользователь с таким именем не зарегистрирован.')
            messages.error(self.request,'Пользователь с таким именем не зарегистрирован.')
        else:
            return email

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        remember_me = self.cleaned_data.get('remember_me')
        if username is not None and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)
        if not remember_me:
            self.request.session.set_expiry(0)
        return self.cleaned_data


class LoginAdminUserForm(AuthenticationForm):

    username = forms.EmailField(label='Електронная почта',
                                help_text='E-mail или ID',
                                widget=forms.EmailInput(attrs={'class': 'form-control has-feedback',
                                                                'id': 'loginform-username',
                                                                'placeholder':'Email'}))
    password = forms.CharField(label='Пароль',
                                help_text='Пароль',
                                widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                    'placeholder':'пароль'}))

    remember_me = forms.BooleanField(required=False,
                                        label='запомнить меня')

    class Meta:
        model = User
        fields = ("username", "password",)


    def clean_username(self):
        email = self.cleaned_data['username']
        current_user = User.objects.filter(email=email)
        if current_user.exists() and current_user[0].is_superuser == False:
            self.add_error('username', 'Этот профиль принадлежит обычному пользователю. Войдите в систему как пользотватель.')
            messages.error(self.request, 'Этот профиль принадлежит обычному пользователю. Войдите в систему как пользотватель.')

        elif current_user.exists() == False:
            self.add_error('username', 'Пользователь с таким именем не зарегистрирован.')
            messages.error(self.request,'Пользователь с таким именем не зарегистрирован.')

        else:
            return email


class SignUpSimpleUserForm(forms.ModelForm):
    email = forms.EmailField(required=True,
                            label="email",
                            widget=forms.EmailInput(attrs={'class': 'form-control',
                                                        'placeholder':'email'}))
    password = forms.CharField(label='Пароль',
                            widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                            'placeholder':'password'})                                                            )
    confirm_password = forms.CharField(label='Пароль(повторно)',
                            widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                            'placeholder':'confirm password'}))
    
    i_agree = forms.BooleanField(required=False,
                                        label='запомнить меня')



    def clean_email(self):
        new_email = self.cleaned_data['email']
        taken_email = User.objects.filter(email=new_email)
        if taken_email.exists():
            print('117 строка формы. КОНФЛИКТ')
            self.add_error('email', 'Пользователь с таким адресом электронной почты уже зарегистрирован')
            # messages.error(self.request,'Пользователь с таким адресом электронной почты уже зарегистрирован')
        return new_email

    def clean_password(self):
        password = self.cleaned_data['password']
        # validate_password(password)
        return password

    def clean(self):
        cleaned_data = super(SignUpSimpleUserForm, self).clean()
        password = cleaned_data.get('password')
        i_agree = cleaned_data.get('i_agree')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            # messages.error(self.request,'Пароль и подтверждения пароля должны совпадать')
            raise forms.ValidationError({
                "password":["Пароль и подтверждения пароля должны совпадать"]
                })
        if i_agree == False:
            # messages.error(self.request,'Вы должны согласиться с политикой конфиденциальности, чтобы зарегистрироваться как жилец')
            raise forms.ValidationError({
                "i_agree":["Вы должны согласиться с политикой конфиденциальности, чтобы зарегистрироваться как жилец"]
            })

    class Meta:
        model = User
        fields = ("email", "password", "confirm_password")