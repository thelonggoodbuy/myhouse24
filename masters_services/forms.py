from django import forms
import datetime
import random


from .models import MastersRequest
from appartments.models import Appartment
from users.models import User
from appartments.models import PersonalAccount


# class RoleWithUserModelChoiceField(forms.ModelChoiceField):
#     def label_from_instance(self, obj):
#         return f'{obj.role.name}: {obj.full_name}'
        # return f'{obj.full_name}'



class MastersRequestsCreateForm(forms.ModelForm):

    owner_utility_field = forms.ModelChoiceField(label='Владелец квартиры', required=False, queryset=None, empty_label='Выберите...',
                             widget=forms.Select(attrs={'class': 'form-control',
                                                        'id': 'owner_utility_field'}))

    class Meta:
        model = MastersRequest
        fields = ['date_work', 'time_work', 'description',
                  'appartment', 'master_type', 'status',
                  'master', 'admin_comment']
        
        labels = {"description": "Описание",
                  "appartment": "Квартира",
                  "master_type": "Тип мастера",
                  "status": "Статус",
                  "master": "Мастер",
                  "admin_comment": "Комментарий"}

        field_classes = {"date_work": forms.CharField,
                         "description": forms.CharField,
                         "appartment": forms.ModelChoiceField,
                         "master_type": forms.ChoiceField,
                         "status": forms.ChoiceField,
                         "master": forms.ModelChoiceField,
                         "admin_comment": forms.CharField}
        

        widgets = {"date_work": forms.TextInput(attrs={"class": "form-control",
                                                       "id": "date_work_field"}),
                   "description": forms.Textarea(attrs={"class": "form-control",
                                                            "id": "description_field",
                                                            "rows": "8"}),
                    "appartment": forms.Select(attrs={"class": "form-control",
                                                      "id": "appartment_field"}),
                    "master_type": forms.Select(attrs={"class": "form-control",
                                                      "id": "master_type_field"}),
                    "status": forms.Select(attrs={"class": "form-control",
                                                  "id": "status_field"}),
                    "master": forms.Select(attrs={"class": "form-control",
                                                  "id": "master_field"}),
                    "admin_comment": forms.Textarea({"class": "form-control",
                                                    "id": "summernote"})
                                                      }

    def __init__(self, *args, **kwargs):
        super(MastersRequestsCreateForm, self).__init__(*args, **kwargs)
        self.fields['owner_utility_field'].queryset = User.objects.filter(owning__isnull=False).distinct()
        self.fields['appartment'].queryset = Appartment.objects.select_related('house').filter(owner_user__isnull=False).distinct()
        self.fields['master'].queryset = User.objects.filter(role__isnull=False)

        if self.instance.id:
            print(str(self.instance.date_work))
            self.initial['date_work'] = datetime.datetime.strptime(str(self.instance.date_work), "%Y-%m-%d").strftime("%d.%m.%Y")


    def clean_date_work(self):
        date_work = self.cleaned_data.get('date_work')
        return datetime.datetime.strptime(date_work, "%d.%m.%Y").strftime("%Y-%m-%d")



