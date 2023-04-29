from django import forms
from .models import UnitOfMeasure, UtilityService, Tariff, TariffCell, CounterReadings
from appartments.models import House, Appartment

from django.db.models import Max
import datetime
import random



class UniteOfMeasureForm(forms.ModelForm):
    title = forms.CharField(label='Ед. изм.', 
                                    required=False, widget=forms.TextInput(attrs={'class': 'form-control',
                                                            'placeholder': 'Ед. изм.'}))

    class Meta:
        model = UnitOfMeasure
        fields = ("title",)

HouseEditeFormSet = forms.modelformset_factory(model=UnitOfMeasure,
                                                    form=UniteOfMeasureForm, 
                                                    can_delete=True, 
                                                    extra=0, 
                                                    )


class UtilityServiceEditeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UtilityServiceEditeForm, self).__init__(*args, **kwargs)
        self.fields['unit_of_measure'].queryset = UnitOfMeasure.objects.all()

    title = forms.CharField(label='Услуги', required=False,
                             widget=forms.TextInput(attrs={'class': 'form-control',
                                                            'placeholder': 'Услуги'}))
    
    unit_of_measure = forms.ModelChoiceField(required=False, label="Единица измерения", queryset=None,
                               widget=forms.Select(attrs={'class':'form-control',
                                                          'id': 'unit_of_measure'}))

    shown_in_counters = forms.BooleanField(required=False, label="Показывать в счетчиках")

    class Meta:
        model = UtilityService
        fields = ("title", "unit_of_measure", "shown_in_counters")

    # def save(self, commit=True):
    #     instance = super(UtilityServiceEditeForm, self).save(commit=False)
    #     print('you changed form!!!')
    #     if commit:
    #         instance.save()
    #     return instance
    


UtilityServiceEditeFormSet = forms.modelformset_factory(model=UtilityService,
                                                        form=UtilityServiceEditeForm, 
                                                        can_delete=True, 
                                                        extra=0, 
                                                        )


class TariffMainForm(forms.ModelForm):

    title = forms.CharField(label='Название тарифа', required=False,
                             widget=forms.TextInput(attrs={'class': 'form-control',
                                                            'placeholder': 'Название'}))

    description = forms.CharField(required=False, label='Описание тарифа',
                        widget=forms.Textarea(attrs={'class':"form-control", 'rows':"5"}))

    class Meta:
        model = Tariff
        fields = ("title", "description")



class TariffCellForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TariffCellForm, self).__init__(*args, **kwargs)
        self.fields['utility_service'].queryset = UtilityService.objects.all()

    utility_service = forms.ModelChoiceField(required=False, label="Услуга", queryset=None,
                               widget=forms.Select(attrs={'class':'form-control',
                                                          'id': 'utility_service'}))

    cost_per_unit = forms.CharField(label='Цена за единицу', required=False,
                             widget=forms.TextInput(attrs={'class': 'form-control',
                                                            'placeholder': 'Цена за единицу'}))
    
    curency = forms.CharField(label='Валюта', required=False,
                             widget=forms.TextInput(attrs={'class': 'form-control',
                                                            'placeholder': 'грн',
                                                            'disabled': ''}))


    class Meta:
        model = TariffCell
        fields = ("utility_service", "cost_per_unit", "curency")


TariffCellFormSet = forms.modelformset_factory(model=TariffCell,
                                                        form=TariffCellForm, 
                                                        can_delete=True, 
                                                        extra=0, 
                                                        )

CreateTariffCellFormSet = forms.inlineformset_factory(Tariff, TariffCell,
                                                        form=TariffCellForm, 
                                                        can_delete=True, 
                                                        extra=0, 
                                                        )



class AddCounterReadingsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AddCounterReadingsForm, self).__init__(*args, **kwargs)
        
        # new_number = CounterReadings.objects.aggregate(Max('number'))['number__max'] + 1

        new_number = random.randint(10000000 , 99999999)
        while CounterReadings.objects.filter(number=new_number):
            new_number = random.randint(10000000 , 99999999)


        
        self.fields['number'].initial = new_number

        # counter усложняет запросы. они начали дублироваться.
        self.fields['utility_service'].queryset = UtilityService.objects.filter(shown_in_counters=True)
        # self.fields['utility_service'].queryset = UtilityService.objects.all()
        # ---------------------------------------------------
        self.fields['house'].queryset = House.objects.all()
        self.fields['status'].choices = CounterReadings.status.field.choices
        self.fields['appartment'].queryset = Appartment.objects.all()

    EMPTY_SECTION_CHOICES = [('', 'Выберите дом')]
    # EMPTY_APPARTMENT_CHOICES = [('', 'Выберите дом')]


    house = forms.ModelChoiceField(label='Дом', required=False, queryset=None, empty_label='Выберите дом',
                             widget=forms.Select(attrs={'class': 'form-control',
                                                        'id': 'house_field'}))
    
    section = forms.ChoiceField(label='Секция', required=False, choices = EMPTY_SECTION_CHOICES,
                             widget=forms.Select(attrs={'class': 'form-control',
                                                        'id': 'section_field'}))
    
    appartment = forms.ModelChoiceField(label='Квартира', required=False, queryset=None,
                             widget=forms.Select(attrs={'class': 'form-control',
                                                        'id': 'appartment_field'}))
    
    utility_service = forms.ModelChoiceField(label='Счетчик', required=False, queryset=None,
                             widget=forms.Select(attrs={'class': 'form-control',
                                                        'id': 'counter_field'}))
    
    status = forms.ChoiceField(label='Статус', required=False,
                             widget=forms.Select(attrs={'class': 'form-control'}))
    
    readings = forms.CharField(label='Показания счетчика', required=False,
                             widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    number = forms.CharField(label='Номер показаний счетчика', required=False,
                            widget=forms.TextInput(attrs={'class': 'form-control',
                                                          'id': 'counter_readings_number'}))
    
    readings = forms.DecimalField(label='показания счетчика', required=False, decimal_places=2,
                                widget=forms.NumberInput(attrs={'class': 'form-control',
                                                          'id': 'counter_readings'}))

    date = forms.DateField(label='дата показаний', initial=datetime.date.today,
                                widget=forms.DateInput(attrs={'class': 'form-control'}))
    class Meta:
        model = CounterReadings
        fields = ['status', 'readings', 'number', 'appartment', 'utility_service', 'date']


    def save(self, commit=True):
        # do something with self.cleaned_data['temp_id']
        print('-------------------------------------------------------------------------------')
        return super(AddCounterReadingsForm, self).save(commit=commit)