from django import forms

from .models import MainPage, SlideBlock, SeoBlock, \
                    AboutUsPage, Document, TariffPage, \
                    ContactPage






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
        

class AboutUsPageUpdateForm(forms.ModelForm):

    class Meta:
        model = AboutUsPage

        fields = ['title', 'short_description', 
                'director_photo', 'addition_title', 
                'addition_short_description']
        
        labels = {'title': 'заголовок',
                  'short_description': 'короткое описание',
                  'director_photo': 'фото директора',
                  'addition_title': 'заголовок',
                  'addition_short_description': 'короткое описание',}
        
        field_classes = {"title": forms.CharField,
                         "short_description": forms.CharField,
                         "director_photo": forms.ImageField,
                         "addition_title": forms.CharField,
                         "addition_short_description": forms.CharField,}
        
        widgets = {"title": forms.TextInput(attrs={"class": "form-control",
                                                   "id": "title_field"}),
                    "short_description": forms.Textarea(attrs={"class": "form-control",
                                                                "id": "short_descriptions_field",
                                                                "rows": "8"}),
                    "director_photo": forms.FileInput,
                    "addition_title": forms.TextInput(attrs={"class": "form-control",
                                                   "id": "title_field"}),
                    "addition_short_description": forms.Textarea(attrs={"class": "form-control",
                                                                "id": "short_descriptions_field",
                                                                "rows": "8"}),
                                                                }





class PhotoGalleryAboutUsSlideForm(forms.ModelForm):
    class Meta:
        model = SlideBlock
        fields = ["image",]
        labels = {"image": "Рекомендуемый размер: (1920x800)",}
        field_classes = {"image": forms.ImageField,}
        widgets = {"image": forms.FileInput,}


    def save(self, commit=True):
        current_form = super(PhotoGalleryAboutUsSlideForm, self).save(commit=False)
        current_form.target = 'about_us_galery'
        current_form.save()



PhotoGalleryAboutUsSlideFormset = forms.modelformset_factory(model=SlideBlock, 
                                                    form=PhotoGalleryAboutUsSlideForm,
                                                    can_delete=True, 
                                                    extra=0)


class AdditionalPhotoGalleryAboutUsSlideForm(forms.ModelForm):

    class Meta:
        model = SlideBlock
        fields = ["image",]
        labels = {"image": "Рекомендуемый размер: (1920x800)",}
        field_classes = {"image": forms.ImageField,}
        widgets = {"image": forms.FileInput,}


    def save(self, commit=True):
        current_form = super(AdditionalPhotoGalleryAboutUsSlideForm, self).save(commit=False)
        current_form.target = 'about_us_addition_galery'
        current_form.save()

AdditionalPhotoGalleryAboutUsSlideFormset = forms.modelformset_factory(model=SlideBlock, 
                                                    form=AdditionalPhotoGalleryAboutUsSlideForm,
                                                    can_delete=True, 
                                                    extra=0)




class DocumentsAboutUsForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["file", "title",]
        labels = {"file": "PDF, JPG (макс. размер 20 Mb)",
                  "title": "Название документа"}
        field_classes = {"file": forms.FileField,
                         "title": forms.CharField}
        widgets = {"file": forms.FileInput(attrs={"id": "title_field"}),
                   "title": forms.TextInput(attrs={"class": "form-control",
                                                   "id": "title_field"})}
        
    def save(self, commit=True):
        current_form = super(DocumentsAboutUsForm, self).save(commit=False)
        current_form.target = 'about_us'
        current_form.save()


DocumentsAboutUsFormset = forms.modelformset_factory(model=Document,
                                                    form=DocumentsAboutUsForm,
                                                    can_delete=True, 
                                                    extra=0)

class UtilitiesUpdateForm(forms.ModelForm):
    class Meta:
        model = SlideBlock
        fields = ["image", "title", "description"]
        labels = {"image": "Рекомендуемый размер: (650x300)",
                  "title": "Название услуги", 
                  "description": "Описание услуги"}
        field_classes = {"image": forms.FileField,
                         "title": forms.CharField,
                         "description": forms.CharField}
        widgets = {"image": forms.FileInput(attrs={"id": "title_field"}),
                   "title": forms.TextInput(attrs={"class": "form-control",
                                                   "id": "title_field"}),
                    "description": forms.Textarea(attrs={"class": "form-control",
                                                        "id": "short_descriptions_field",
                                                        "rows": "8"})}
        
    def save(self, commit=True):
        current_form = super(UtilitiesUpdateForm, self).save(commit=False)
        current_form.target = 'services'
        current_form.save()

UtilitiesUpdateFormSet = forms.modelformset_factory(model=SlideBlock,
                                                    form=UtilitiesUpdateForm,
                                                    can_delete=True,
                                                    extra=0)


class TariffPageUpdateForm(forms.ModelForm):

    class Meta:
        model = TariffPage

        fields = ['title', 'description',]
        
        labels = {'title': 'заголовок',
                  'description': 'короткий текст',}
        
        field_classes = {"title": forms.CharField,
                         "description": forms.CharField,}
        
        widgets = {"title": forms.TextInput(attrs={"class": "form-control",
                                                   "id": "title_field"}),
                    "description": forms.Textarea(attrs={"class": "form-control",
                                                                "id": "short_descriptions_field",
                                                                "rows": "8"}),}


class TariffCellUpdateForm(forms.ModelForm):
    class Meta:
        model = SlideBlock
        fields = ["image", "title"]
        labels = {"image": "Файл",
                  "title": "Подпись",}
        field_classes = {"image": forms.FileField,
                         "title": forms.CharField,}
        widgets = {"image": forms.FileInput(attrs={"id": "title_field"}),
                   "title": forms.TextInput(attrs={"class": "form-control",
                                                   "id": "title_field"}),}
        
    def save(self, commit=True):
        current_form = super(TariffCellUpdateForm, self).save(commit=False)
        current_form.target = 'tariff'
        current_form.save()




TariffCellUpdateFormSet = forms.modelformset_factory(model=SlideBlock,
                                                    form=TariffCellUpdateForm,
                                                    can_delete=True,
                                                    extra=0)




class ContactUpdateForm(forms.ModelForm):
    class Meta:
        model = ContactPage
        fields = ["title", "simple_text", "link_to_commercial_cite",\
                "full_name", "location", "address",\
                "phone", "email",\
                "map_code"]
        labels = {"title": "Заголовок",
                  "simple_text":"Краткий текст",
                  "link_to_commercial_cite": "Ссылка на комерческий сайт",
                  "full_name": "ФИО",
                  "location": "Локация",
                  "address": "Адрес",
                  "phone": "Телефон",
                  "email": "E-mail",
                  "map_code": "Код карты"}
        field_classes = {"title": forms.CharField,
                        "simple_text": forms.CharField,
                        "link_to_commercial_cite": forms.CharField,
                        "full_name": forms.CharField,
                        "location": forms.CharField,
                        "address": forms.CharField,
                        "phone": forms.CharField,
                        "email": forms.CharField,
                        "map_code": forms.CharField}
        widgets = {"title": forms.TextInput(attrs={"class": "form-control",
                                                   "id": "title_field"}),
                    "simple_text": forms.Textarea(attrs={"class": "form-control",
                                                                "id": "short_descriptions_field",
                                                                "rows": "8"}),
                    "link_to_commercial_cite": forms.TextInput(attrs={"class": "form-control",
                                                                    "id": "link_to_commercial_cite_field"}),
                    "full_name": forms.TextInput(attrs={"class": "form-control",
                                                        "id": "full_name_field"}),
                    "location": forms.TextInput(attrs={"class": "form-control",
                                                        "id": "location_field"}),
                    "address": forms.TextInput(attrs={"class": "form-control",
                                                        "id": "address_field"}),
                    "phone": forms.TextInput(attrs={"class": "form-control",
                                                        "id": "phone_field"}),
                    "email": forms.TextInput(attrs={"class": "form-control",
                                                        "id": "email_field"}),
                    "map_code": forms.TextInput(attrs={"class": "form-control",
                                                        "id": "map_code_field"}),}