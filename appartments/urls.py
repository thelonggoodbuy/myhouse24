from django.urls import path

from .views import ReportView, HousesListView, HouseDeleteView, HouseEditeView, HouseDetailView


app_name='appartments'

urlpatterns = [
    path('report_view/', ReportView.as_view(), name='report_view'),

    # house CRUD
    path('houses_list/', HousesListView.as_view(), name='houses_list'),
    path('house_delete/', HouseDeleteView.as_view(), name='houses_delete'),
    path('house_delete/<int:pk>', HouseDeleteView.as_view(), name='houses_delete'),
    path('house_edit/', HouseEditeView.as_view(), name="house_edit"),
    path('house_edit/<int:pk>', HouseEditeView.as_view(), name="house_edit"), 
    path('house_detail/', HouseDetailView.as_view(), name="house_detail"),
    path('house_detail/<int:pk>', HouseDetailView.as_view(), name="house_detail"),


]