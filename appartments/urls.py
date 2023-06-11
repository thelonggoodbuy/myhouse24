from django.urls import path

from .views import ReportView,\
                    HousesListView, HouseDeleteView, HouseEditeView, HouseDetailView,\
                    AppartmentsListView, AppartmentsCardView, AppartmentDeleteView, AppartmentEditeView, AppartmentCreateView,\
                    PersonalAccountsListView, PersonalAccountAddView, PersonalAccountEditeView, PersonalAccountDeleteView, personal_accounts_print_all,\
                    OwnersListView, OwnerCardView, OwnerEditeView, OwnerDeleteView, CreteNewUser, OwnerSendInvitation


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
    path('appartment_create/', AppartmentCreateView.as_view(), name="appartment_create"),
    path('appartment_detail/<int:pk>', AppartmentsCardView.as_view(), name="appartment_detail"),
    path('appartment_delete/', AppartmentDeleteView.as_view(), name='appartment_delete'),
    path('appartment_delete/<int:pk>', AppartmentDeleteView.as_view(), name='appartment_delete'),
    path('appartment_edite/', AppartmentEditeView.as_view(), name='appartment_edite'),
    path('appartment_edite/<int:pk>', AppartmentEditeView.as_view(), name='appartment_edite'),

    # personal accounts CRUD
    path('personal_accounts_list/', PersonalAccountsListView.as_view(), name="personal_accounts_list"),
    path('personal_accounts_create/', PersonalAccountAddView.as_view(), name="personal_accounts_create"),
    path('personal_accounts_edite/', PersonalAccountEditeView.as_view(), name="personal_accounts_edite"),
    path('personal_accounts_edite/<int:pk>', PersonalAccountEditeView.as_view(), name="personal_accounts_edite"),
    path('personal_account_delete/', PersonalAccountDeleteView.as_view(), name="personal_account_delete"),
    path('personal_account_delete/<int:pk>', PersonalAccountDeleteView.as_view(), name="personal_account_delete"),
    path('personal_accounts_print_all/', personal_accounts_print_all, name="personal_accounts_print_all"),
    # PersonalAccountDeleteView

    # owners CRUD
    path('owners_list/', OwnersListView.as_view(), name="owner_list"),
    path('owners_detail/', OwnerCardView.as_view(), name="owner_detail"),
    path('owners_detail/<int:pk>', OwnerCardView.as_view(), name="owner_detail"),
    path('owner_edite/', OwnerEditeView.as_view(), name="owner_edite"),
    path('owner_edite/<int:pk>', OwnerEditeView.as_view(), name="owner_edite"),
    path('owner_delete/', OwnerDeleteView.as_view(), name="owner_delete"),
    path('owner_delete/<int:pk>', OwnerDeleteView.as_view(), name="owner_delete"),
    path('owner_create', CreteNewUser.as_view(), name="owner_create"),
    path('owner_send_invitation/', OwnerSendInvitation.as_view(), name="owner_send_invitation"),
]