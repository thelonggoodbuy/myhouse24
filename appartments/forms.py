from django import forms
from .models import House, HouseAdditionalImage, Section, Floor, PersonalAccount
from users.models import User
from .models import Appartment
from django.db.models import Q
from django.core.exceptions import ValidationError


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
        # self.fields['floor'] = Floor.objects.select_related('house').all()

        self.fields['floor'].queryset =  Floor.objects.select_related('house').all()
        # self.fields['personal_account_choice'].queryset = PersonalAccount.objects.filter(status = 'active')



    # HOUSE_CHOICES = House.objects.all()
    # USERS_CHOICE = User.objects.all()
    # SECTIONS_CHOICES = Section.objects.all()
    # FLOORS_CHOICES = Floor.objects.all()


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
    
    # personal_account = forms.CharField(required=False, label="Лицевой счет",
    #                            widget=forms.TextInput(attrs={'class':'form-control'}))

    # personal_account_choice = forms.ModelChoiceField(required=False, label="Лицевой счет", queryset=None,
    #                            widget=forms.Select(attrs={'class':'form-control'}))

    class Meta:
        model = Appartment
        fields = ("number", "area", "house", "sections", "floor",\
                  "owner_user")
    
  

class AppartmentPersonalAccountEditeForm(forms.ModelForm):
    # def __init__(self, *args, **kwargs):
    #         super(AppartmentEditeForm, self).__init__(*args, **kwargs)
    #         self.fields['personal_account_choice'].queryset = PersonalAccount.objects.filter(status = 'active')


    number = forms.CharField(required=False, label="Лицевой счет",
                               widget=forms.TextInput(attrs={'class':'form-control',
                                                             'id': 'personal_account_number'}))
    
    class Meta:
        model = PersonalAccount
        fields = ('number',)