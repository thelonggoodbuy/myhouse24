from django import forms
from .models import UnitOfMeasure, UtilityService, Tariff, TariffCell




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
    # measure_unit = forms.ChoiceField(label='Ед. изм.', required=False, choices=['None', ],
    #                                  widget=forms.Select(attrs={'class':'form-control',
    #                                                             'id': 'measure_unit',
    #                                                             'disabled': ''}))

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