from django import forms
from .models import House, HouseAdditionalImage, Section, Floor, PersonalAccount
from users.models import User, Role
from .models import Appartment
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.password_validation import validate_password
from django.utils.html import strip_tags


from django.utils.html import format_html
from django.utils.safestring import mark_safe

from django_select2 import forms as s2forms

class HouseEditeForm(forms.ModelForm):

    title = forms.CharField(required=False, label="Название дома",
                            widget=forms.TextInput(attrs={'class': 'form-control',
                                                            'placeholder': 'Название дома'}))
    
    address = forms.CharField(required=False, label="Адресс дома",
                            widget=forms.TextInput(attrs={'class': 'form-control',
                                                            'placeholder': 'Адресс кинотеатра'}))
    
    main_image = forms.ImageField(label='Изображение #1. Размер: (522x350)', 
                                  required=False, widget=forms.FileInput)

    class Meta:
        model = House
        fields = ("title", "address", "main_image")


# -----------------------------house: simple images-------------------------------
class HouseEditeFormImage(forms.ModelForm):
    image = forms.ImageField(label='Изображение. Размер: (248x160)', 
                                    required=False, widget=forms.FileInput)

    

    class Meta:
        model = HouseAdditionalImage
        fields = ("image",)


HouseEditeFormSetImage = forms.modelformset_factory(model=HouseAdditionalImage, 
                                                    form=HouseEditeFormImage, 
                                                    can_delete=False, 
                                                    extra=0, 
                                                    min_num=4, 
                                                    max_num=4)

# -------------------------------sections----------------------------------------
class SectionForm(forms.ModelForm):
    title = forms.CharField(required=False, label="Название",
                            widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Section
        fields = ("title",)

SectionEditeFormSet = forms.inlineformset_factory(House,
                                                    Section,
                                                    form=SectionForm,
                                                    can_delete=True,
                                                    extra=0, 
                                                    min_num=0)

class FloorForm(forms.ModelForm):
    title = forms.CharField(required=False, label="Название",
                            widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Floor
        fields = ("title",)

FloorEditeFormSet = forms.inlineformset_factory(House,
                                                Floor,
                                                form=FloorForm,
                                                can_delete=True,
                                                extra=0,
                                                min_num=0)


        
class ResponsibilitiesForm(forms.Form):
    responsibilities = forms.ModelChoiceField(required=False,label="ФИО",
                                            queryset=User.objects.filter(Q(role__isnull=False)),
                                            widget=forms.Select(attrs={'class': 'form-control',
                                                                       'id': 'responsible_field'})
                                         )
    
    role = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": "form-control", "readonly":""}))

    DELETE = forms.BooleanField(required=False)


ResponsibilitiesEditeFormset = forms.formset_factory(form = ResponsibilitiesForm, 
                                                        extra=0, 
                                                        min_num=1, 
                                                        )



class AppartmentEditeForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(AppartmentEditeForm, self).__init__(*args, **kwargs)
        
        self.fields['house'].queryset = House.objects.all()
        self.fields['owner_user'].queryset = User.objects.all()
        self.fields['sections'].queryset = Section.objects.select_related('house').all()
        self.fields['floor'].queryset =  Floor.objects.select_related('house').all()
    

    number = forms.CharField(required=False, label="Номер квартиры",
                            widget=forms.TextInput(attrs={'class': 'form-control',
                                                            'placeholder': 'Номер квартиры'}))
    
    area = forms.CharField(required=False, label="Площадь (кв.м.)",
                            widget=forms.TextInput(attrs={'class': 'form-control',
                                                            'placeholder': 'Площадь (кв.м.)'}))
    
    house = forms.ModelChoiceField(required=False, label="Дом", queryset=None,
                               widget=forms.Select(attrs={'class':'form-control',
                                                          'id': 'house_dropdown'}))
    
    sections = forms.ModelChoiceField(required=False, label="Секция", queryset=None,
                               widget=forms.Select(attrs={'class':'form-control'}))
    
    floor = forms.ModelChoiceField(required=False, label="Этаж", queryset=None,
                               widget=forms.Select(attrs={'class':'form-control'}))
    
    owner_user = forms.ModelChoiceField(required=False, label="Владелец квартиры", queryset=None,
                               widget=forms.Select(attrs={'class':'form-control', 'id': 'owner_field'}))
    
    class Meta:
        model = Appartment
        fields = ("number", "area", "house", "sections", "floor",\
                  "owner_user")
    
  

class AppartmentPersonalAccountEditeForm(forms.ModelForm):


    number = forms.CharField(required=False, label="Лицевой счет",
                               widget=forms.TextInput(attrs={'class':'form-control',
                                                             'id': 'personal_account_number'}))
    
    class Meta:
        model = PersonalAccount
        fields = ('number',)



class OwnerUpdateForm(forms.ModelForm):

    status_tupple = User.get_users_status_tupple()

    id = forms.CharField(required=False, label="ID",
                            widget=forms.TextInput(attrs={'class': 'form-control',
                                                            'placeholder': 'имя'}))

    name = forms.CharField(required=False, label="Имя",
                            widget=forms.TextInput(attrs={'class': 'form-control',
                                                            'placeholder': 'имя'}))

    surname = forms.CharField(required=False, label="Фамилия",
                            widget=forms.TextInput(attrs={'class': 'form-control',
                                                            'placeholder': 'фамилия'}))
    
    patronymic = forms.CharField(required=False, label="Отчество",
                        widget=forms.TextInput(attrs={'class': 'form-control',
                                                        'placeholder': 'отчество'}))
    
    image = forms.ImageField(label='Сменить изображения', 
                                  required=False, widget=forms.FileInput())
    
    burn = forms.DateField(required=False, input_formats=['%d.%m.%Y'], label="Дата рождения",
                        widget=forms.DateInput(format='%d.%m.%Y',attrs={'class': 'form-control',
                                                        'placeholder': 'дата рождения'}))

    phone = forms.CharField(required=False, label="телефон",
                        widget=forms.TextInput(attrs={'class': 'form-control',
                                                    'placeholder':'номер телефона'}))
    
    viber = forms.CharField(required=False, label="viber",
                        widget=forms.TextInput(attrs={'class': 'form-control',
                                                    'placeholder':'viber'}))
    
    telegram = forms.CharField(required=False, label="telegram",
                    widget=forms.TextInput(attrs={'class': 'form-control',
                                                'placeholder':'telegram'}))
    
    role = forms.ModelChoiceField(required=False, label="роль", 
                                    queryset=Role.objects.all(),
                                    widget=forms.Select(attrs={'class':'form-control'}))

    status = forms.ChoiceField(required=True, label="статус", choices=status_tupple,
                               widget=forms.Select(attrs={'class':'form-control'}))

    email = forms.EmailField(required=False, label="email(логин)",
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
    
    note = forms.CharField(required=False, label='заметки',
                        widget=forms.Textarea(attrs={'class':"form-control", 'rows':"12"}))


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
        cleaned_data = super(OwnerUpdateForm, self).clean()
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
        current_form = super(OwnerUpdateForm, self).save(commit=False)
        current_form_cleaned = super(OwnerUpdateForm, self).clean()
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
        fields = ("name", "surname", "patronymic",\
                "burn", "phone", "viber",\
                "telegram", "email", "role",\
                "status", "password", "confirm_password",\
                "image", "id", "note",)
