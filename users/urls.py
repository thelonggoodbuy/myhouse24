from django.urls import path
from .models import sign_in
app_name='users'

urlpatterns = [
    path('sign_in/', sign_in, name='sign_in'),
]