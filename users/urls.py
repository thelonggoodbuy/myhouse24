from django.urls import path
from .views import LoginSimpleUser, LoginAdminUser, LogOutUser



app_name='users'


urlpatterns = [
    path('login_user/', LoginSimpleUser.as_view(), name='login_user'),
    path('login_admin/', LoginAdminUser.as_view(), name='login_admin'),
    path('logout/', LogOutUser.as_view(), name='logout'),
]