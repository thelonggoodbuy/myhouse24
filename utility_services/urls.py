from django.urls import path


from .views import UtilityAndMeasuresUnitsEditeList,\
                     TariffListView, TariffEditeView, TariffCreateView, TariffDeleteView, TariffCopyView,\
                     CounterListView, CounterReadingsPerAppartmentListView, AddCounterReadingsView, AddCounterReadingsPerCounterView


app_name='utility_services'


urlpatterns = [
    path('report_view/', UtilityAndMeasuresUnitsEditeList.as_view(), name='report_view'),
    # tariff logic
    path('tariff_list/', TariffListView.as_view(), name="tariff_list"),
    path('tariff_edite/', TariffEditeView.as_view(), name="tariff_edite"),
    path('tariff_edite/<int:pk>', TariffEditeView.as_view(), name="tariff_edite"),
    path('tariff_create/', TariffCreateView.as_view(), name="tariff_create"),
    path('tariff_delete', TariffDeleteView.as_view(), name="tariff_delete"),
    path('tariff_delete/<int:pk>', TariffDeleteView.as_view(), name="tariff_delete"),
    path('tariff_clone/', TariffCopyView.as_view(), name="tariff_clone"),
    path('tariff_clone/<int:pk>', TariffCopyView.as_view(), name="tariff_clone"),

    path('counter_list/', CounterListView.as_view(), name="counter_list"),

    path('counter_readings_per_appartment_list_view/', CounterReadingsPerAppartmentListView.as_view(), name="counter_readings_per_appartment_list_view"),
    path('counter_readings_per_appartment_list_view/<int:pk>', CounterReadingsPerAppartmentListView.as_view(), name="counter_readings_per_appartment_list_view"),
    path('add_counter_readings/', AddCounterReadingsView.as_view(), name="add_counter_readings"),

    path('add_counter_readings_per_conter/', AddCounterReadingsPerCounterView.as_view(), name="add_counter_readings_per_counter"),
    path('add_counter_readings_per_conter/<int:pk>', AddCounterReadingsPerCounterView.as_view(), name="add_counter_readings_per_counter"),
    ]