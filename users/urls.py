from django.urls import path, re_path
from .views import LoginSimpleUser, LoginAdminUser, LogOutUser, SignUpSimpleUser, ActivateAccount, \
                    AdminSettingsUsersListLogic, AdminSettingsUserCardView, AdminSettingsUsersDeleteView, AdmSettingsUsersUpdateView,\
                    AdminSettingsUsersRolesView, AppartmentsOwnersView,\
                    PermissionDeniedView, MessagesListView, MessageCreateView, MessageDetailView, MessageDeleteView,\
                    ProfileDetailView, ProfileStatisticPerAppartment, ProfileReceiptListView, ProfileReceiptListPerAppartmentView,\
                    ProfileTariffListView, ProfileMessageListView, ProfileMessageDetailView, ProfileMessageDeleteView,\
                    ProfileMastersRequestListView, ProfileMasterRequestDeleteView, ProfileMastersRequestsCreateView, ProfileUserDetail
                        # temp_funct_users_listlogic



app_name='users'


urlpatterns = [
    # ************authentication logic url*************************
    path('login_user/', LoginSimpleUser.as_view(), name='login_user'),
    path('login_admin/', LoginAdminUser.as_view(), name='login_admin'),

    path('sign_up_user/', SignUpSimpleUser.as_view(), name='sign_up_user'),
    path('activate/<uidb64>/<token>/', ActivateAccount.as_view(), name='activate'),

    path('logout/', LogOutUser.as_view(), name='logout'),

    # **************users settings by admin*************************
    path('admin_settings_users_list/', AdminSettingsUsersListLogic.as_view(), name='admin_settings_users_list'),
    #---------------------------------вот очень сомнительный кусок дальше. узнать в среду-----------------------------
    #следующий путь возможно удалю. решение выглядит как то сомнительно: две ссылки сразу - но по другому не получается
    # JS генерить ссылки на вьюшку с параметром. Выдает ошибки.
    path('admin_settings_users_card/', AdminSettingsUserCardView.as_view(), name='admin_settings_users_card'), 
    path('admin_settings_users_card/<int:pk>/', AdminSettingsUserCardView.as_view(), name='admin_settings_users_card'),
    # re_path(r'^admin_settings_users_card/(?P<pk>[0-9]+)/$', AdminSettingsUserCardView.as_view(), name='admin_settings_users_card'),
    #---------------------------------конец очень сомнительного куса кода---------------------------------------------
    path('admin_settings_users_delete/', AdminSettingsUsersDeleteView.as_view(), name='admin_settings_users_delete'),
    path('admin_settings_users_delete/<int:pk>/', AdminSettingsUsersDeleteView.as_view(), name='admin_settings_users_delete'),

    path('admin_settings_users_update/', AdmSettingsUsersUpdateView.as_view(), name='adm_settings_users_update'),
    path('admin_settings_users_update/<int:pk>/', AdmSettingsUsersUpdateView.as_view(), name='adm_settings_users_update'),
    # roles
    path('admin_settings_users_roles/', AdminSettingsUsersRolesView.as_view(), name='adm_settings_users_roles'),

    path('appartments_owners/', AppartmentsOwnersView.as_view(), name='appartments_owners'),
    path('permission_denide/', PermissionDeniedView.as_view(), name='permission_denied'),

    path('message_list_view/', MessagesListView.as_view(), name='message_list_view'),
    path('message_create/', MessageCreateView.as_view(), name='message_create'),
    path('message_detail/', MessageDetailView.as_view(), name='message_detail'),
    path('message_detail/<int:pk>/', MessageDetailView.as_view(), name='message_detail'),
    # path('message_delete/', MessageDeleteView.as_view(), name="message_delete"),
    path('message_delete/<int:pk>/', MessageDeleteView.as_view(), name="message_delete"),

    # urls for CABINET LOGIC
    path('profile_detail/', ProfileDetailView.as_view(), name='profile_detail'),
    path('profile_statistic_per_appartment/<int:pk>/', ProfileStatisticPerAppartment.as_view(), name="profile_statistic_per_appartment"),
    path('profile_receipt_list/', ProfileReceiptListView.as_view(), name='profile_receipt_list'),
    path('profile_receipt_list_per_appartment/', ProfileReceiptListPerAppartmentView.as_view(), name='profile_receipt_list_per_appartment'),
    path('profile_receipt_list_per_appartment/<int:pk>/', ProfileReceiptListPerAppartmentView.as_view(), name='profile_receipt_list_per_appartment'),
    path('profile_tariff_list/<int:pk>/', ProfileTariffListView.as_view(), name='profile_tariff_list'),
    path('profile_message_list/', ProfileMessageListView.as_view(), name='profile_message_list'),
    path('profile_message_list/<int:pk>/', ProfileMessageListView.as_view(), name='profile_message_list'),
    path('profile_message_detail/', ProfileMessageDetailView.as_view(), name="profile_message_detail"),
    path('profile_message_detail/<int:pk>/', ProfileMessageDetailView.as_view(), name="profile_message_detail"),
    path('profile_message_delete/<int:pk>/', ProfileMessageDeleteView.as_view(), name="profile_message_delete"),

    path('profile_masters_request_list_view/', ProfileMastersRequestListView.as_view(), name="profile_masters_request_list_view"),
    path('profile_masters_request_list_view/<int:pk>/', ProfileMastersRequestListView.as_view(), name="profile_masters_request_list_view"),

    path('profile_master_request_delete/', ProfileMasterRequestDeleteView.as_view(), name="profile_master_request_delete"),
    path('profile_master_request_delete/<int:pk>/', ProfileMasterRequestDeleteView.as_view(), name="profile_master_request_delete"),

    path('profile_masters_requests_create/', ProfileMastersRequestsCreateView.as_view(), name="profile_masters_requests_create"),

    path('profile_user_detail/<int:pk>/',  ProfileUserDetail.as_view(), name="profile_user_detail"),
]