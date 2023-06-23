from django import forms
import datetime
from django.db.models import Max
import random


from .models import Receipt, ReceiptCell, Requisite
                                    # ,ReceiptTemplate
from appartments.models import Appartment
from utility_services.models import Tariff, UtilityService, UnitOfMeasure
from appartments.models import House


class AddReceiptForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AddReceiptForm, self).__init__(*args, **kwargs)

        new_number = random.randint(10000000000 , 99999999999)
        while Receipt.objects.filter(number=new_number):
            new_number = random.randint(10000000000 , 99999999999)

        self.fields['number'].initial = new_number
        self.fields['appartment'].queryset = Appartment.objects.all()
        self.fields['tariff'].queryset = Tariff.objects.all()

    RECEIPT_STATUS = (
        ('paid_for', 'Оплачена'),
        ('partly', 'Частично'),
        ('unpaid', 'Неоплачена'),
    )

    number = forms.CharField(label='Номер', required=False,
                            widget=forms.TextInput(attrs={'class': 'form-control',
                                                          'id': 'receipt_readings_number'}))

    payment_due = forms.DateField(label='дата квитанции', initial=datetime.date.today,
                                widget=forms.DateInput(attrs={'class': 'form-control'}))
    
    appartment = forms.ModelChoiceField(label='Квартира', required=False, queryset=None, empty_label='Выберите дом',
                             widget=forms.Select(attrs={'class': 'form-control',
                                                        'id': 'appartment_field'}))

    payment_was_made = forms.BooleanField(label='Проведена', required=False)

    status = forms.ChoiceField(label='Статус', required=False, choices=RECEIPT_STATUS,
                             widget=forms.Select(attrs={'class': 'form-control',
                                                        'id': 'status_field'}))
    
    tariff = forms.ModelChoiceField(label='Тариф', required=False, queryset=None, empty_label='Выберите',
                             widget=forms.Select(attrs={'class': 'form-control',
                                                        'id': 'tariff_field'}))
    
    from_date = forms.DateField(label='Период с', initial=datetime.date.today,
                                widget=forms.DateInput(attrs={'class': 'form-control'}))
    
    to_date = forms.DateField(label='Период до', initial=datetime.date.today,
                                widget=forms.DateInput(attrs={'class': 'form-control'}))
    
    total_sum = forms.DecimalField(label='Общая сумма', required=False, 
                                decimal_places=2, initial=00.00,
                                widget=forms.NumberInput(attrs={'class': 'form-control',
                                                          'id': 'total_summ'}))

    class Meta:
        model = Receipt
        fields = ['number', 'payment_due', 'appartment',\
                'payment_was_made', 'status', 'tariff',\
                    'from_date', 'to_date', 'total_sum']


class UtilityReceiptForm(forms.Form):

    EMPTY_HOUSE_CHOICES = [('', 'Выберите дом')]
    EMPTY_SECTION_CHOICES = [('', 'Выберите дом')]

    house = forms.ModelChoiceField(required=False,label="дом", empty_label='Выберите дом',
                                            queryset=House.objects.all(),
                                            widget=forms.Select(attrs={'class': 'form-control',
                                                                       'id': 'house_utility_field'}))
    
    section = forms.ChoiceField(label='секция', required=False, choices=EMPTY_HOUSE_CHOICES,
                            widget=forms.Select(attrs={'class': 'form-control',
                                                       'id': 'section_utility_field'}))
    
    personal_account = forms.CharField(label='лицевой счет', required=False,
                            widget=forms.TextInput(attrs={'class': 'form-control',
                                                       'id': 'personal_account_utility_field'}))
    


class ReceiptCellForm(forms.ModelForm):


    utility_service = forms.ModelChoiceField(required=False, label="Услуга", empty_label='Выберите...',
                                            queryset=UtilityService.objects.all(),
                                            widget=forms.Select(attrs={'class': 'form-control',
                                                                       'id': 'utility_servive_field'}))
    
    consumption = forms.DecimalField(label='Расход', required=False, decimal_places=2,
                                widget=forms.NumberInput(attrs={'class': 'form-control',
                                                          'id': 'consumption_field'}))
    
    unit_of_measure = forms.ModelChoiceField(required=False, label="Ед. изм.", empty_label='Выберите...',
                                             
                                            queryset=UnitOfMeasure.objects.all(),
                                            widget=forms.Select(attrs={'class': 'form-control',
                                                                       'id': 'unite_of_measure_field'}))

    cost_per_unit = forms.DecimalField(label='Цена за ед., грн.', required=False, decimal_places=2,
                                widget=forms.NumberInput(attrs={'class': 'form-control',
                                                          'id': 'cost_per_unit_field'}))
    
    cost = forms.DecimalField(label='Стоимость, грн.', required=False, decimal_places=2,
                                widget=forms.NumberInput(attrs={'class': 'form-control',
                                                          'id': 'cost_field',
                                                          'old_cost': '00.00'}))

    class Meta:
        model = ReceiptCell
        fields = ('utility_service', 'consumption', 'unit_of_measure', 'cost_per_unit', 'cost')


# ReceiptCellFormset = forms.inlineformset_factory(Receipt, ReceiptCell, form=ReceiptCellForm, fk_name='receipt', can_delete=True, extra=1, min_num=0)
ReceiptCellFormset = forms.inlineformset_factory(Receipt, 
                                                ReceiptCell, 
                                                form=ReceiptCellForm,
                                                fields =['utility_service', 'consumption', 'unit_of_measure', 'cost_per_unit', 'cost', 'receipt'],
                                                fk_name='receipt',
                                                can_delete=True,
                                                extra=0,
                                                min_num=0)


# class ReceiptTemplateListForm(forms.Form):

#     TEMPLATE_CHOICES = []
#     DEFAULT_TEMPLATE = None
#     receipts = ReceiptTemplate.objects.filter().order_by('id').values( 'id', 'name', 'is_default')
#     for receipt in receipts:
#         template_cell = (receipt['id'], receipt['name'])
#         TEMPLATE_CHOICES.append(template_cell)
#         if receipt['is_default'] == True: DEFAULT_TEMPLATE = receipt['id'] 

    
#     templates_list = forms.ChoiceField(required=True, label="Шаблон", choices=TEMPLATE_CHOICES, initial=DEFAULT_TEMPLATE,
#                                             widget=forms.RadioSelect(attrs={'class': 'form-check-input'}))
    


# class ReceiptTeplateEditeForm(forms.ModelForm):

#     name = forms.CharField(label='название шаблона', required=False,
#                             widget=forms.TextInput(attrs={'class': 'form-control',
#                                                             'id': 'template_name'}))
    
#     receipt_template = forms.FileField(label='Загрузить пользовательский шаблон', required=False)



#     class Meta:
#         model = ReceiptTemplate
#         fields = ('name', 'receipt_template', 'is_default')



# ReceiptTeplateEditeFormSet = forms.modelformset_factory(model=ReceiptTemplate,
#                                                         form=ReceiptTeplateEditeForm, 
#                                                         can_delete=True, 
#                                                         # extra=1
#                                                         )



class RequisiteUpdateForm(forms.ModelForm):

    class Meta:
        model = Requisite
        fields = ("company_title", "description",)
        labels = {"company_title": "Название компании",
                  "description": "Описание"}
        field_classes = {"company_title": forms.CharField,
                        "description": forms.CharField}
        widgets = {"company_title": forms.TextInput(attrs={"class": "form-control"}),
                        "description": forms.Textarea(attrs={'class':'form-control', 'rows':"6"})}