from django.urls import path

from .views import MainPageUpdateView, AboutUsUpdateView, UtilitiesUpdateView,\
                    TariffUpdateView, ContactUpdateView,\
                    FrontMainPageView, FrontAboutUsView




app_name='website'

urlpatterns = [
    # back end logic
    path('main_page_update_view/', MainPageUpdateView.as_view(), name='main_page_update_view'),
    path('about_us_page_update_view/', AboutUsUpdateView.as_view(), name='about_us_page_update_view'),
    path('utilities_update_view/', UtilitiesUpdateView.as_view(), name='utilities_update_view'),
    path('tariff_update_view/', TariffUpdateView.as_view(), name='tariff_update_view'),
    path('contact_update_view/', ContactUpdateView.as_view(), name='contact_update_view'),

    # front end logic
    path('main_page/', FrontMainPageView.as_view(), name='main_page'),
    path('front_about_us/', FrontAboutUsView.as_view(), name='front_about_us'),
]