from django.urls import path
from .views import MastersRequestsListView


app_name='masters_services'



urlpatterns = [
    path('masters_requests_list/', MastersRequestsListView.as_view(), name='masters_requests_list'),
    ]