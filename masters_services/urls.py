from django.urls import path
from .views import MastersRequestsListView, MastersRequestsCreateView, MastersRequestsEditeView, MastersRequestsDeleteView


app_name='masters_services'



urlpatterns = [
    path('masters_requests_list/', MastersRequestsListView.as_view(), name='masters_requests_list'),
    path('masters_requests_create/', MastersRequestsCreateView.as_view(), name='masters_requests_create'),
    path('masters_requests_update/', MastersRequestsEditeView.as_view(), name='masters_requests_update'),
    path('masters_requests_update/<int:pk>', MastersRequestsEditeView.as_view(), name='masters_requests_update'),
    path('masters_requests_delete/', MastersRequestsDeleteView.as_view(), name='masters_requests_delete'),
    path('masters_requests_delete/<int:pk>', MastersRequestsDeleteView.as_view(), name='masters_requests_delete'),
    
    ]