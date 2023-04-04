from django import forms
from .models import UnitOfMeasure, UtilityService




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