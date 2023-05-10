from django import forms
import datetime
import random


from .models import Statement, PaymentItem
from users.models import User
from appartments.models import PersonalAccount


class StatementArrivalCreateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(StatementArrivalCreateForm, self).__init__(*args, **kwargs)

        new_number = random.randint(10000000000 , 99999999999)
        while Statement.objects.filter(number=new_number):
            new_number = random.randint(10000000000 , 99999999999)

        self.fields['number'].initial = new_number  
        
        self.fields['owner'].queryset = User.objects.filter(owning__isnull=False).distinct()
        # if self.instance: self.fields['owner'].initial = self.instance.personal_account.appartment_account.owner_user.full_name

        self.fields['personal_account'].queryset = PersonalAccount.objects.all().distinct()
        self.fields['type_of_paynent_item'].queryset = PaymentItem.objects.filter(type='arrive')
        self.fields['manager'].queryset = User.objects.filter(role__isnull=False).distinct()


    number = forms.CharField(label='Номер', required=False, 
                            widget=forms.TextInput(attrs={'class': 'form-control',
                                                          'id': 'statement_number'}))

    date = forms.DateField(label='дата квитанции', initial=datetime.date.today,
                                widget=forms.DateInput(attrs={'class': 'form-control',
                                                              'id': 'date_field'}))

    owner = forms.ModelChoiceField(label='Владелец квартиры', required=False, queryset=None, empty_label='Выберите...',
                             widget=forms.Select(attrs={'class': 'form-control',
                                                        'id': 'owner_field'}))

    personal_account = forms.ModelChoiceField(label='Лицевой счет', required=False, queryset=None, empty_label='Выберите...',
                             widget=forms.Select(attrs={'class': 'form-control',
                                                        'id': 'personal_account_field'}))

    type_of_paynent_item = forms.ModelChoiceField(label='Статья', required=False, queryset=None, empty_label='Выберите...',
                             widget=forms.Select(attrs={'class': 'form-control',
                                                        'id': 'type_of_paynent_item_field'}))

    summ = forms.DecimalField(label='Сумма', required=False, 
                                decimal_places=2, initial=00.00,
                                widget=forms.NumberInput(attrs={'class': 'form-control',
                                                          'id': 'summ_field'}))

    checked = forms.BooleanField(label='Проведен', required=False)

    manager = forms.ModelChoiceField(label='Менедежер', required=False, queryset=None, empty_label='Выберите...',
                             widget=forms.Select(attrs={'class': 'form-control',
                                                        'id': 'management_field'}))

    comment = forms.CharField(required=False, label='Комментарий',
                        widget=forms.Textarea(attrs={'class':'form-control', 'rows':"6"}))


    class Meta:
        model = Statement
        # fields = ['number', 'date', 'personal_account']
        fields = ['number', 'date', 'personal_account',\
                        'type_of_paynent_item', 'summ', 'checked',\
                        'manager', 'comment']