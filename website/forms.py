from django import forms

from .models import MainPage, SlideBlock, SeoBlock






class MainPageUpdateForm(forms.ModelForm):


    class Meta:
        model = MainPage
        fields = ['title', 'short_descriptions', 'show_app_link']
        labels = {'title': 'заголовок',
                  'short_descriptions': 'короткое описание',
                  'show_app_link': 'показать ссылки на приложения'}
        field_classes = {"title": forms.CharField,
                         "short_descriptions": forms.CharField}
        widgets = {"title": forms.TextInput(attrs={"class": "form-control",
                                                   "id": "title_field"}),
                    "short_descriptions": forms.Textarea(attrs={"class": "form-control",
                                                                "id": "short_descriptions_field",
                                                                "rows": "8"})}
        

class MainSlideForm(forms.ModelForm):

    class Meta:
        model = SlideBlock
        fields = ["image",]
        labels = {"image": "Рекомендуемый размер: (1920x800)"}
        field_classes = {"image": forms.FileField}
        widgets = {"image": forms.FileInput}

    def save(self, commit=True):
        current_form = super(MainSlideForm, self).save(commit=False)
        current_form.target = 'main_page_slider'
        current_form.save()


MainSliderFormset = forms.modelformset_factory(model=SlideBlock, 
                                                    form=MainSlideForm, 
                                                    can_delete=False, 
                                                    extra=0, 
                                                    min_num=3, 
                                                    max_num=3)



class RoundUsSlideForm(forms.ModelForm):

    class Meta:
        model = SlideBlock
        fields = ["image", "title", "description"]
        labels = {"image": "Рекомендуемый размер: (1920x800)",
                  "title": "Заголовок", 
                  "description": "Описание"}
        field_classes = {"image": forms.ImageField,
                         "title": forms.CharField,
                         "description": forms.CharField}
        widgets = {"image": forms.FileInput,
                   "title": forms.TextInput(attrs={"class": "form-control",
                                                   "id": "title_field"}),
                    "description": forms.Textarea(attrs={"class": "form-control",
                                                        "id": "short_descriptions_field",
                                                        "rows": "4"})}

    def save(self, commit=True):
        current_form = super(RoundUsSlideForm, self).save(commit=False)
        current_form.target = 'main_page_around'
        current_form.save()


RoundUsSliderFormset = forms.modelformset_factory(model=SlideBlock, 
                                                    form=RoundUsSlideForm, 
                                                    can_delete=False, 
                                                    extra=0, 
                                                    min_num=6, 
                                                    max_num=6)


class SeoBlockForm(forms.ModelForm):

    class Meta:
        model = SeoBlock
        fields = ['title', 'description', 'keyword']
        labels = {'title': 'Title',
                  'description': 'Description',
                  'keyword': 'Keywords'}
        field_classes = {"title": forms.CharField,
                         "description": forms.CharField,
                         "keyword": forms.CharField}
        widgets = {"title": forms.TextInput(attrs={"class": "form-control",
                                                   "id": "title_field"}),
                   "description": forms.Textarea(attrs={"class": "form-control",
                                                   "id": "description",
                                                   "rows": "4"}),
                    "keyword": forms.Textarea(attrs={"class": "form-control",
                                                        "id": "keyword_field",
                                                        "rows": "4"})}