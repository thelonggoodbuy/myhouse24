from copy import deepcopy

from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import F

from django.http import HttpResponseRedirect

from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.views.generic.edit import DeleteView, FormView, UpdateView


from .models import House, HouseAdditionalImage, Section
from .forms import HouseEditeForm, HouseEditeFormSetImage, SectionEditeFormSet


# view for testing role using
class ReportView(TemplateView):
    
    template_name = "appartments/cabinet_report_per_appartment.html"

# ------------------------------------------------------------------
# -----------------Houses CRUID-------------------------------------
# ------------------------------------------------------------------
class HousesListView(ListView):
    model = House
    context_object_name = 'houses_list'
    template_name = 'appartments/houses_list.html'


class HouseDeleteView(DeleteView):

    model = House
    success_url = reverse_lazy('appartments:houses_list')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        house_title = self.object.title
        success_url = self.get_success_url()
        self.object.delete()
        messages.success(request, (f"Дом  '{ house_title }'. Удален."))
        return HttpResponseRedirect(success_url)
    


class HouseEditeView(UpdateView):
    form_class = HouseEditeForm
    model = House
    template_name = "appartments/house_edit.html"
    success_url = reverse_lazy('appartments:houses_list')

 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        additiona_images = HouseAdditionalImage.objects.select_related('house').filter(house=self.object)
        context['simple_images_formset'] = HouseEditeFormSetImage(queryset=additiona_images, prefix='simple_images_formset')

        sections = Section.objects.select_related('house').filter(house=self.object)
        # print(sections)
        context['section_formset'] = SectionEditeFormSet(queryset=sections, prefix="section_formset")

        # SectionEditeFormSet
        return context

    def post(self, request, *args, **Kwargs):
        main_form = HouseEditeForm(request.POST, request.FILES, instance=self.get_object())
        addition_images_formset = HouseEditeFormSetImage(request.POST, request.FILES, queryset=HouseAdditionalImage.objects.filter(house=self.get_object()), prefix='simple_images_formset')
        sections_formset = SectionEditeFormSet(request.POST, queryset=Section.objects.select_related('house').filter(house=self.get_object()), prefix="section_formset")
        if main_form.is_valid() and addition_images_formset.is_valid() and sections_formset.is_valid():
            return self.form_valid(main_form, addition_images_formset, sections_formset)
        else:
            print('------------------------SMTH WRONG-----------------------')
            print(main_form.errors)
            print(addition_images_formset.errors)
            print(sections_formset.errors)

    def form_valid(self, main_form, addition_images_formset, sections_formset):
        
        house = main_form.save(commit=False)
        house_images_formset = addition_images_formset.save(commit=False)
        current_section_formset = sections_formset.save(commit=False)

        for image in house_images_formset:
            image.house = house
            image.save()
        

        

        for section in current_section_formset:
            section.house = house
            section.save()

        # for section in current_section_formset:
        #     # print(section)
        #     # section.house = self.get_object().id
        #     section.house = 
        #     # print(section)
        #     section.save()

        house.save()
        success_url = self.success_url
        messages.success(self.request, f"Данные о доме {self.get_object().title} обновлены.")
        return HttpResponseRedirect(success_url)