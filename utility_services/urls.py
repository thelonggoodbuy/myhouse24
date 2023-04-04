from django.urls import path


from .views import UtilityAndMeasuresUnitsEditeList


app_name='utility_services'


urlpatterns = [
    path('report_view/', UtilityAndMeasuresUnitsEditeList.as_view(), name='report_view'),
    ]