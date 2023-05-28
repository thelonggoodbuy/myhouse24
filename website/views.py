from django.shortcuts import render

from .models import MainPage, SlideBlock, SeoBlock, AboutUsPage, Document, ServicesPage, ContactPage
from .forms import MainPageUpdateForm, MainSliderFormset, RoundUsSliderFormset, SeoBlockForm,\
                    AboutUsPageUpdateForm, PhotoGalleryAboutUsSlideFormset,\
                    AdditionalPhotoGalleryAboutUsSlideFormset, DocumentsAboutUsFormset,\
                    UtilitiesUpdateForm, UtilitiesUpdateFormSet, TariffPageUpdateForm, TariffPage,\
                    TariffCellUpdateFormSet, ContactUpdateForm

from django.views.generic.edit import UpdateView, FormView

from django.views.generic.base import TemplateView

from django.urls import reverse_lazy

from django.contrib import messages

from django.http import HttpResponseRedirect


class MainPageUpdateView(FormView):

    template_name = 'website/main_page_update.html'
    form_class = MainPageUpdateForm
    model = MainPage
    success_url = reverse_lazy('website:main_page_update_view')
    main_slider_images = SlideBlock.objects.filter(target='main_page_slider')
    round_us_slider_formset = SlideBlock.objects.filter(target='main_page_around')

    def post(self, request, *args, **Kwargs): 
        main_form = MainPageUpdateForm(request.POST, instance=MainPage.objects.first(), prefix="main_form")
        main_slider_formset = MainSliderFormset(request.POST, request.FILES, queryset=self.main_slider_images, prefix='main_slider_formset')
        round_us_slider_formset = RoundUsSliderFormset(request.POST, request.FILES, queryset=self.round_us_slider_formset, prefix='round_us_slider_formset')
        seo_block_form = SeoBlockForm(request.POST, instance=MainPage.objects.first().seo_block, prefix='seo_block_form')


        if main_form.is_valid() and main_slider_formset.is_valid() and round_us_slider_formset.is_valid() and seo_block_form.is_valid():
            return self.form_valid(main_form, main_slider_formset, round_us_slider_formset, seo_block_form)
        else:
            if main_form.errors:
                for field, error in main_form.errors.items():
                    print(f'{field}: {error}')

            if main_slider_formset.errors:
                for form in main_slider_formset:
                    for field, error in main_form.errors.items():
                        print(f'{field}: {error}')

            if round_us_slider_formset.errors:
                for form in round_us_slider_formset:
                    for field, error in main_form.errors.items():
                        print(f'{field}: {error}')

            if seo_block_form.errors:
                for field, error in seo_block_form.errors.items():
                    print(f'{field}: {error}')



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try: 
            context['main_form'] = MainPageUpdateForm(instance=MainPage.objects.first(), prefix="main_form")
        except:
            main_form_instance = MainPage.objects.create()
            context['main_form'] = MainPageUpdateForm(instance=main_form_instance, prefix="main_form")

        context['main_slider_formset'] = MainSliderFormset(queryset=self.main_slider_images, prefix='main_slider_formset')
        context['round_us_slider_formset'] = RoundUsSliderFormset(queryset=self.round_us_slider_formset, prefix='round_us_slider_formset')
        context['seo_block_form'] = SeoBlockForm(instance=MainPage.objects.first().seo_block, prefix='seo_block_form')

        return context
    

    def form_valid(self, main_form, main_slider_formset, round_us_slider_formset, seo_block_form):
        main_page = main_form.save(commit=False)
        seo_block = seo_block_form.save()
        main_page.seo_block = seo_block
        main_page.save()

        main_slider_formset.save()
        round_us_slider_formset.save()

        success_url = self.success_url
        messages.success(self.request, f"Изменения в главную страницу внесены!")
        return HttpResponseRedirect(success_url)
    

class AboutUsUpdateView(FormView):
    template_name = 'website/about_us_page_update.html'
    form_class = AboutUsPageUpdateForm
    model = AboutUsPage
    success_url = reverse_lazy('website:about_us_page_update_view')
    photo_gallery_about_us_formset = SlideBlock.objects.filter(target='about_us_galery')
    photo_gallery_additional_about_us_formset = SlideBlock.objects.filter(target='about_us_addition_galery')
    documents = Document.objects.filter(target = 'about_us')



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try: 
            context['main_form'] = AboutUsPageUpdateForm(instance=AboutUsPage.objects.first(), prefix="main_form")
        except:
            about_us_form_instance = AboutUsPage.objects.create()
            context['main_form'] = AboutUsPageUpdateForm(instance=about_us_form_instance, prefix="main_form")

        context['photo_gallery_about_us_formset'] = PhotoGalleryAboutUsSlideFormset(queryset=self.photo_gallery_about_us_formset, 
                                                                                    prefix='photo_gallery_about_us_formset')
        
        context['additional_gallery_about_us_formset'] = AdditionalPhotoGalleryAboutUsSlideFormset(queryset=self.photo_gallery_additional_about_us_formset, 
                                                                                    prefix='additional_gallery_about_us_formset')
        
        context['documents_about_us_formset'] = DocumentsAboutUsFormset(queryset=self.documents, prefix='documents_about_us_formset')

        context['seo_block_form'] = SeoBlockForm(instance=AboutUsPage.objects.first().seo_block, prefix='seo_block_form')
        return context
    

    def post(self, request, *args, **Kwargs): 
        main_form =  AboutUsPageUpdateForm(request.POST, request.FILES, instance=AboutUsPage.objects.first(), prefix="main_form")
        photo_gallery_about_us_formset = PhotoGalleryAboutUsSlideFormset(request.POST, request.FILES, 
                                                                         queryset=self.photo_gallery_about_us_formset, 
                                                                         prefix='photo_gallery_about_us_formset')
        additional_gallery_about_us_formset = AdditionalPhotoGalleryAboutUsSlideFormset(request.POST, request.FILES, 
                                                                            queryset=self.photo_gallery_additional_about_us_formset, 
                                                                            prefix='additional_gallery_about_us_formset')
        documents_about_us_formset = DocumentsAboutUsFormset(request.POST, request.FILES, queryset=self.documents, 
                                                             prefix='documents_about_us_formset')
        seo_block_form = SeoBlockForm(request.POST, instance=AboutUsPage.objects.first().seo_block, prefix='seo_block_form')

        if main_form.is_valid() and \
            photo_gallery_about_us_formset.is_valid() and \
            additional_gallery_about_us_formset.is_valid() and \
            documents_about_us_formset.is_valid() and\
            seo_block_form.is_valid():
            return self.form_valid(main_form, photo_gallery_about_us_formset, \
                                   additional_gallery_about_us_formset, \
                                    documents_about_us_formset, seo_block_form)
        else:
            print('--------------SMTH--------WRONG-----------')
            if main_form.errors:
                for field, error in main_form.errors.items():
                    print(f'{field}: {error}')
            if photo_gallery_about_us_formset.errors:
                for form in photo_gallery_about_us_formset:
                    for field, error in form.errors.items():
                        print(f'{field}: {error}')
            if additional_gallery_about_us_formset.errors:
                for form in additional_gallery_about_us_formset:
                    for field, error in form.errors.items():
                        print(f'{field}: {error}')

            if documents_about_us_formset.is_valid() == False:
                print('-------------ERORROR!!---------------')
                for form in documents_about_us_formset:
                    
                    for field, error in form.errors.items():
                        print(f'{field}: {error}')
            if seo_block_form.errors:
                for field, error in seo_block_form.errors.items():
                    print(f'{field}: {error}')

    def form_valid(self, main_form, photo_gallery_about_us_formset,\
                    additional_gallery_about_us_formset, \
                    documents_about_us_formset, seo_block_form):

        about_us_page = main_form.save(commit=False)
        photo_gallery_about_us_formset.save()
        additional_gallery_about_us_formset.save()
        documents_about_us_formset.save()
        seo = seo_block_form.save()
        about_us_page.seo_block = seo

        about_us_page.save()

        success_url = self.success_url
        messages.success(self.request, f"Изменения в 'Страницу о нас' внесены!")
        return HttpResponseRedirect(success_url)
    


class UtilitiesUpdateView(FormView):
    template_name = 'website/utilities_update.html'
    form_class = UtilitiesUpdateForm
    model = ServicesPage
    success_url = reverse_lazy('website:utilities_update_view')
    utilities_about_us_formset_queryset = SlideBlock.objects.filter(target='services')
    service_page = None


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['utilities_formset'] = UtilitiesUpdateFormSet(queryset=self.utilities_about_us_formset_queryset, 
                                                                                    prefix='utilities_formset')
        
        self.service_page = ServicesPage.objects.first()
        if self.service_page != None:
            self.service_page = ServicesPage.objects.first()
        else:
            service_page = ServicesPage.objects.create()
            service_page.save()
            self.service_page = service_page


        context['seo_block_form'] = SeoBlockForm(instance=self.service_page.seo_block, prefix='seo_block_form')
        return context

    def post(self, request, *args, **Kwargs): 
        
        utilities_formset = UtilitiesUpdateFormSet(request.POST, request.FILES, 
                                                            queryset=self.utilities_about_us_formset_queryset, 
                                                            prefix='utilities_formset')

        seo_block_form = SeoBlockForm(request.POST, instance=ServicesPage.objects.first().seo_block, prefix='seo_block_form')

        if utilities_formset.is_valid() and seo_block_form.is_valid():
            return self.form_valid(utilities_formset, seo_block_form)
        else:
            print(utilities_formset.errors)
            print(utilities_formset.non_form_errors())
            if utilities_formset.errors:
                for form in utilities_formset:
                    print(form.errors)
                    for field, error in form.errors.items():
                        print(f'{field}: {error}')
            if seo_block_form.errors:
                for field, error in seo_block_form.errors.items():
                    print(f'{field}: {error}')
    def form_valid(self, utilities_formset, seo_block_form):

        utilities_formset.save()
        service_pave = ServicesPage.objects.first()
        seo = seo_block_form.save()
        service_pave.seo_block = seo
        service_pave.save()
        success_url = self.success_url
        messages.success(self.request, f"Изменения в 'услуги' внесены!")
        return HttpResponseRedirect(success_url)
    

class TariffUpdateView(FormView):
    template_name = 'website/tariff_update.html'
    form_class = TariffPageUpdateForm
    model = TariffPage
    tariff_cell_formset_queryset = SlideBlock.objects.filter(target='tariff')
    tariff_page = None
    success_url = reverse_lazy('website:tariff_update_view')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if TariffPage.objects.first() == None:
            tariff_page = TariffPage.objects.create()
            tariff_page.save()
        context['main_form'] = TariffPageUpdateForm(instance=TariffPage.objects.first(), prefix="main_form")
        context['tariff_cell_formset'] = TariffCellUpdateFormSet(queryset=self.tariff_cell_formset_queryset, prefix="tariff_formset")
        context['seo_block_form'] = SeoBlockForm(instance=TariffPage.objects.first().seo_block, prefix='seo_block_form')
        return context

    def post(self, request, *args, **Kwargs):         
        main_form = TariffPageUpdateForm(request.POST, instance=TariffPage.objects.first(), prefix="main_form")
        tariff_cell_formset = TariffCellUpdateFormSet(request.POST, request.FILES, queryset=self.tariff_cell_formset_queryset, prefix="tariff_formset")
        seo_block_form = SeoBlockForm(request.POST, instance=TariffPage.objects.first().seo_block, prefix='seo_block_form')
        if main_form.is_valid() and tariff_cell_formset.is_valid() and seo_block_form.is_valid():
            return self.form_valid(main_form, tariff_cell_formset, seo_block_form)
        else:
            if main_form.errors:
                for field, error in main_form.errors.items():
                    print(f'{field}: {error}')
            if tariff_cell_formset.errors:
                for form in tariff_cell_formset:
                    for field, error in form.errors.items():
                        print(f'{field}: {error}')
            if seo_block_form.errors:
                for field, error in seo_block_form.errors.items():
                    print(f'{field}: {error}')

    def form_valid(self, main_form, tariff_cell_formset, seo_block_form):
        tariff_cell_formset.save()
        tariff = main_form.save(commit=False)
        seo = seo_block_form.save()
        tariff.seo_block = seo
        tariff.save()
        success_url = self.success_url
        messages.success(self.request, f"Изменения в 'тарифы' внесены!")
        return HttpResponseRedirect(success_url)
    


class ContactUpdateView(FormView):
    template_name = 'website/contact_update.html'
    form_class = ContactUpdateForm
    model = ContactPage
    success_url = reverse_lazy('website:contact_update_view')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if ContactPage.objects.first() == None:
            contact_page = ContactPage.objects.create()
            contact_page.save()
        context['main_form'] = ContactUpdateForm(instance=ContactPage.objects.first(), prefix="main_form")
        context['seo_block_form'] = SeoBlockForm(instance=ContactPage.objects.first().seo_block, prefix='seo_block_form')
        return context


    def post(self, request, *args, **Kwargs):         
        main_form = ContactUpdateForm(request.POST, instance=ContactPage.objects.first(), prefix="main_form")
        seo_block_form = SeoBlockForm(request.POST, instance=ContactPage.objects.first().seo_block, prefix='seo_block_form')
        if main_form.is_valid() and seo_block_form.is_valid():
            return self.form_valid(main_form, seo_block_form)
        else:
            if main_form.errors:
                for field, error in main_form.errors.items():
                    print(f'{field}: {error}')
            if seo_block_form.errors:
                for field, error in seo_block_form.errors.items():
                    print(f'{field}: {error}')


    def form_valid(self, main_form, seo_block_form):
        contacts = main_form.save(commit=False)
        seo = seo_block_form.save()
        contacts.seo_block = seo
        contacts.save()
        success_url = self.success_url
        messages.success(self.request, f"Изменения в страница 'контактов' внесены!")
        return HttpResponseRedirect(success_url)