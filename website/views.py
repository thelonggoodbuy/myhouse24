from django.shortcuts import render

from .models import MainPage, SlideBlock, SeoBlock
from .forms import MainPageUpdateForm, MainSliderFormset, RoundUsSliderFormset, SeoBlockForm

from django.views.generic.edit import UpdateView, FormView

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