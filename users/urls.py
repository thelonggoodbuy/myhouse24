from django.urls import path
from .views import LoginSimpleUser, LoginAdminUser, LogOutUser, SignUpSimpleUser, ActivateAccount



app_name='users'


urlpatterns = [
    path('login_user/', LoginSimpleUser.as_view(), name='login_user'),
    path('login_admin/', LoginAdminUser.as_view(), name='login_admin'),

    path('sign_up_user/', SignUpSimpleUser.as_view(), name='sign_up_user'),
    path('activate/<uidb64>/<token>/', ActivateAccount.as_view(), name='activate'),

    path('logout/', LogOutUser.as_view(), name='logout'),
]