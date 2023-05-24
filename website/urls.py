from django.urls import path

from .views import MainPageUpdateView




app_name='website'

urlpatterns = [
    path('main_page_update_view/', MainPageUpdateView.as_view(), name='main_page_update_view'),
]