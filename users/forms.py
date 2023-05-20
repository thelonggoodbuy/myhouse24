from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist
from django.utils.html import strip_tags
import datetime
from django.db.models import Q

from .models import User, Role, MessageToUser
from appartments.models import House, Section, Floor, Appartment




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
        if current_user.exists() and current_user[0].is_staff == False:
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
            self.add_error('email', 'Пользователь с таким адресом электронной почты уже зарегистрирован')
        return new_email

    def clean_password(self):
        password = self.cleaned_data['password']
        validate_password(password)
        return password

    def clean(self):
        cleaned_data = super(SignUpSimpleUserForm, self).clean()
        password = cleaned_data.get('password')
        i_agree = cleaned_data.get('i_agree')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError({
                "password":["Пароль и подтверждения пароля должны совпадать"]
                })
        if i_agree == False:
            raise forms.ValidationError({
                "i_agree":["Вы должны согласиться с политикой конфиденциальности, чтобы зарегистрироваться как жилец"]
            })

    class Meta:
        model = User
        fields = ("email", "password", "confirm_password")



class AdminSettingsUsersUpdateForm(forms.ModelForm):
    status_tupple = User.get_users_status_tupple()

    name = forms.CharField(required=False, label="Имя",
                            widget=forms.TextInput(attrs={'class': 'form-control',
                                                            'placeholder': 'имя'}))

    surname = forms.CharField(required=False, label="Фамилия",
                            widget=forms.TextInput(attrs={'class': 'form-control',
                                                            'placeholder': 'фамилия'}))

    phone = forms.CharField(required=False, label="телефон",
                        widget=forms.TextInput(attrs={'class': 'form-control',
                                                    'placeholder':'номер телефона'}))
    
    role = forms.ModelChoiceField(required=False, label="роль", 
                                    queryset=Role.objects.all(),
                                    widget=forms.Select(attrs={'class':'form-control'}))

    status = forms.ChoiceField(required=True, label="статус", choices=status_tupple,
                               widget=forms.Select(attrs={'class':'form-control'}))

    email = forms.EmailField(required=False, label="email",
                            widget=forms.EmailInput(attrs={'class': 'form-control',
                                                        'placeholder':'email'}))
    
    password = forms.CharField(required=False, label='Пароль',
                    widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                    'placeholder':'password',
                                                    'id': 'password'}))
                                            
    confirm_password = forms.CharField(required=False, label='Повторите пароль',
                        widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                        'placeholder':'password',
                                                        'id': 'confirm_password'}))


    def clean_email(self):
        try:
            email = self.cleaned_data['email']
        except ObjectDoesNotExist:
            pass
        else:
            other_user = User.objects.get(email=email)
            if other_user and other_user.id != self.instance.id:
                self.data = self.data.copy()
                self.data['email'] = self.instance.email
                raise forms.ValidationError("Один из пользователей системы уже использует такой email")
        finally:
            return email

    def clean(self):
        cleaned_data = super(AdminSettingsUsersUpdateForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if self.cleaned_data['password'] != '':
            password = self.cleaned_data['password']
            validate_password(password)

        if password != confirm_password:
            raise forms.ValidationError({
                "password":["Пароли не совпадают"]
                })
        
    def save(self, commit=True):
        current_form = super(AdminSettingsUsersUpdateForm, self).save(commit=False)
        current_form_cleaned = super(AdminSettingsUsersUpdateForm, self).clean()
        if commit:
            if current_form_cleaned['password'] == '':
                current_form.save(update_fields=["name", "surname", "phone", \
                                            "role", "status", "email"])
            else:
                current_form.set_password(current_form_cleaned['password'])
                current_form.save()
                subject="Пароль для МойДом24 изменен"
                message = render_to_string('email_templates/change_password.html', {
                    'user_email': current_form_cleaned['email'],
                    'user_new_password': current_form_cleaned['password'],
                })
                plain_message = strip_tags(message)
                self.instance.email_user(subject, plain_message)
        return current_form
        
    class Meta:
        model = User
        fields = ("name", "surname", "phone", "email",\
                    "role", "status", "password", "confirm_password")

    
class AdminSettingsUsersRolesCellForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ("id", "statistic_permission", "fund_permission", "receipt_permission",
                    "accounts_permission", "appartments_permission", "owners_permission", 
                    "house_permission", "messages_permission", "masters_request_permission",
                    "counter_permission", "site_managing_permission", "utility_services_permission",
                    "tarif_permission", "role_section_permission", "users_sections_permission", "requisite_sections_permission")


UsersRolesFormSet = forms.modelformset_factory(model=Role, form=AdminSettingsUsersRolesCellForm, can_delete=False, extra=0)


class MessageToUserForm(forms.ModelForm):
    for_users_with_debt = forms.BooleanField(required=False, label="Владельцам с долгами",
                            widget=forms.CheckboxInput)
    house = forms.ModelChoiceField(label='Дом', required=False, queryset=None, empty_label='Выберите дом',
                             widget=forms.Select(attrs={'class': 'form-control',
                                                        'id': 'house_utility_field'}))
    
    sections = forms.ModelChoiceField(label='Секция', required=False, queryset=None, empty_label='Выберите дом',
                             widget=forms.Select(attrs={'class': 'form-control',
                                                        'id': 'sections_utility_field'}))
    floor = forms.ModelChoiceField(label='Этаж', required=False, queryset=None, empty_label='Выберите дом',
                             widget=forms.Select(attrs={'class': 'form-control',
                                                        'id': 'floor_utility_field'}))
    appartment = forms.ModelChoiceField(label='Квартира', required=False, queryset=None, empty_label='Выберите дом',
                             widget=forms.Select(attrs={'class': 'form-control',
                                                        'id': 'appartment_utility_field'}))

    class Meta:
        model = MessageToUser
        fields = ('topic', 'text', 'message_target_type')
        labels = {
            'topic': 'заголовок',
            'text': 'текст сообщения',
        }
        field_classes = {
            'topic': forms.CharField,
            'text': forms.CharField,
            'message_target_type': forms.ModelChoiceField,
        }
        widgets = {
            "topic": forms.TextInput(attrs={"class": "form-control"}),
            "text": forms.Textarea(attrs={"class": "form-control",
                                          "id": "summernote",
                                          "rows": "6"}),
            "message_target_type": forms.RadioSelect(),
                    }
        
    def __init__(self, *args, **kwargs):
        
        super(MessageToUserForm, self).__init__(*args, **kwargs)

        self.fields['house'].queryset = House.objects.all()
        self.fields['sections'].queryset = Section.objects.all()
        self.fields['floor'].queryset = Floor.objects.all()
        self.fields['appartment'].queryset = Appartment.objects.filter(owner_user__isnull=False)

    def save(self, commit=True):
        message = super(MessageToUserForm, self).save(commit=False)
        message_form_data = super(MessageToUserForm, self).clean()
        message.date_time = datetime.datetime.now()
        message.save()
        Q_debtor_list = []

        if message_form_data['message_target_type'] == "one_user":
            item_user = message_form_data['appartment'].owner_user
            message.to_users.add(item_user)

        elif message_form_data['message_target_type'] == "all_users":
            if message_form_data['for_users_with_debt'] == True: 
                Q_debtor_list.append(Q(owning__isnull=False))
                Q_debtor_list.append(Q(owning__personal_account__balance__lt=0))
            owners = User.objects.filter(*Q_debtor_list)
            # print(owners)
            for owner in owners:
                
                message.to_users.add(owner)
        
        else:
            if message_form_data['message_target_type'] == "all_users_per_house":
                item_owners = list(message_form_data['house'].related_appartment.filter(owner_user__isnull=False).values('owner_user'))
                
            if message_form_data['message_target_type'] == "all_users_per_floor":
                item_owners = list(message_form_data['floor'].related_appartment.filter(owner_user__isnull=False).values('owner_user'))

            if message_form_data['message_target_type'] == "all_users_per_sections":
                item_owners = list(message_form_data['sections'].related_appartment.filter(owner_user__isnull=False).values('owner_user'))

            

            if message_form_data['for_users_with_debt'] == True: 
                Q_debtor_list.append(Q(owning__isnull=False))
                Q_debtor_list.append(Q(owning__personal_account__balance__lt=0))

            list_of_users_id = [user_dict['owner_user'] for user_dict in item_owners]
            Q_debtor_list.append(Q(id__in = list_of_users_id))
            owners = User.objects.filter(*Q_debtor_list)
            print(owners)
            for owner in owners:
                message.to_users.add(owner)


        message.save()
        response = message

        


        return response