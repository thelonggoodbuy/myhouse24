from django.urls import path
from .views import LoginSimpleUser, LoginAdminUser, LogOutUser, SignUpSimpleUser, ActivateAccount, \
                    AdminSettingsUsersListLogic \
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
    # path('temp_funct_users_listlogic/', temp_funct_users_listlogic, name='temp_funct_users_listlogic'),
]