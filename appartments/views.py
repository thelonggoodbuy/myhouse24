from copy import deepcopy

from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import F
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse

from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.views.generic.edit import DeleteView, FormView, UpdateView
from django.views.generic.detail import DetailView




from .models import House, HouseAdditionalImage, Section
from users.models import User

from .forms import HouseEditeForm, HouseEditeFormSetImage, SectionEditeFormSet, FloorEditeFormSet, ResponsibilitiesEditeFormset


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
   
    initial_responsibility = []

    def get(self, request, *args, **kwargs):
        if self.request.is_ajax() and self.request.method == 'GET':
            # print(self.request.GET['choosen_user'])
            user_id = self.request.GET['choosen_user']
            user = User.objects.get(id=user_id)
            user_role = user.role.name
            response = {'user_id': user_role}
            print(response)
            return JsonResponse(response, safe=False)
        else:
            self.object = self.get_object()
            return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        additiona_images = HouseAdditionalImage.objects.select_related('house').filter(house=self.object)
        context['simple_images_formset'] = HouseEditeFormSetImage(queryset=additiona_images, prefix='simple_images_formset')
        context['section_formset'] = SectionEditeFormSet(instance=self.get_object(), prefix="section_formset")
        context['floor_formset'] = FloorEditeFormSet(instance=self.get_object(), prefix="floor_formset")

        self.__class__.initial_responsibility = []
        for responsibility in self.object.responsibilities.filter(Q(role__isnull=False)): 
            self.__class__.initial_responsibility.append({'responsibilities': responsibility, 'role': responsibility.role})
        context['responsibilities_formset'] = ResponsibilitiesEditeFormset(initial=self.__class__.initial_responsibility, prefix="responsibility_formset")
        return context

    def post(self, request, *args, **Kwargs):
        main_form = HouseEditeForm(request.POST, request.FILES, instance=self.get_object())
        addition_images_formset = HouseEditeFormSetImage(request.POST, request.FILES, queryset=HouseAdditionalImage.objects.filter(house=self.get_object()), prefix='simple_images_formset')
        sections_formset = SectionEditeFormSet(request.POST, instance=self.get_object(), prefix="section_formset")
        floor_formset = FloorEditeFormSet(request.POST, instance=self.get_object(), prefix="floor_formset")
        responsibilities_formset = ResponsibilitiesEditeFormset(request.POST, initial=self.__class__.initial_responsibility, prefix="responsibility_formset")

        if main_form.is_valid()\
                            and addition_images_formset.is_valid()\
                            and sections_formset.is_valid()\
                            and floor_formset.is_valid()\
                            and responsibilities_formset.is_valid():
            
            return self.form_valid(main_form,\
                                addition_images_formset,\
                                sections_formset,\
                                floor_formset,\
                                responsibilities_formset)
        else:
            print('------------------------SMTH WRONG-----------------------')
            print(main_form.errors)
            print(addition_images_formset.errors)
            print(sections_formset.errors)
            print(responsibilities_formset.errors)

    def form_valid(self,\
                main_form,\
                addition_images_formset,\
                sections_formset,\
                floor_formset,\
                responsibilities_formset):
        
        house = main_form.save(commit=False)
        house_images_formset = addition_images_formset.save(commit=False)

        for image in house_images_formset:
            image.house = house
            image.save()
        
        sections_formset.save()

        floor_formset.save()

        responsibility_queryset = []
        for responsibility in responsibilities_formset:
            if responsibility.cleaned_data.get('DELETE') == True:
              house.responsibilities.remove(responsibility.cleaned_data.get('responsibilities'))
            else: 
                choosen_user = responsibility.cleaned_data.get('responsibilities')
                # print(choosen_user)
                if choosen_user != None: responsibility_queryset.append(choosen_user)
        house.responsibilities.set(responsibility_queryset)        

        house.save()
        success_url = self.success_url
        messages.success(self.request, f"Данные о доме {self.get_object().title} обновлены.")
        return HttpResponseRedirect(success_url)
    

class HouseDetailView(DetailView):
    # model = House
    queryset = House.objects.select_related().all()
    template_name = "appartments/house_detail.html"
    context_object_name = 'house'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        # context['users'] = User.objects.select_related('role').filter(responsibilities=self.get_object())
        
        context['responsibility_users'] = self.get_object().responsibilities.select_related('role').filter()
        # print(self.get_object().responsibilities.select_related('role').filter())

        return context