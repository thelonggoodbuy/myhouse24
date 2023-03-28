from django.urls import path

from .views import ReportView,\
                     HousesListView, HouseDeleteView, HouseEditeView, HouseDetailView,\
                     AppartmentsListView, AppartmentsCardView, AppartmentDeleteView, AppartmentEditeView,\
                     PersonalAccountsListView


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

    # appartments CRUD
    path('appartments_list/', AppartmentsListView.as_view(), name="appartments_list"),
    path('appartment_detail/', AppartmentsCardView.as_view(), name="appartment_detail"),
    path('appartment_detail/<int:pk>', AppartmentsCardView.as_view(), name="appartment_detail"),
    path('appartment_delete/', AppartmentDeleteView.as_view(), name='appartment_delete'),
    path('appartment_delete/<int:pk>', AppartmentDeleteView.as_view(), name='appartment_delete'),
    path('appartment_edite/', AppartmentEditeView.as_view(), name='appartment_edite'),
    path('appartment_edite/<int:pk>', AppartmentEditeView.as_view(), name='appartment_edite'),

    # personal accounts CRUD
    path('personal_accounts_list/', PersonalAccountsListView.as_view(), name="personal_accounts_list"),

]