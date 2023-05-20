from django.urls import path, re_path
from .views import LoginSimpleUser, LoginAdminUser, LogOutUser, SignUpSimpleUser, ActivateAccount, \
                    AdminSettingsUsersListLogic, AdminSettingsUserCardView, AdminSettingsUsersDeleteView, AdmSettingsUsersUpdateView,\
                    AdminSettingsUsersRolesView, AppartmentsOwnersView,\
                    PermissionDeniedView, MessagesListView, MessageCreateView, MessageDetailView, MessageDeleteView
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
]