from django.urls import path

from .views import StatementListView, StatementArrivalCreateView, StatementExpenseCreateView, StatementUpdateView


app_name='statements'

urlpatterns = [
    path('statements_list/', StatementListView.as_view(), name='statements_list'),
    path('statement_arrival_create/', StatementArrivalCreateView.as_view(), name='statement_arrival_create'),
    path('statement_expense_create/', StatementExpenseCreateView.as_view(), name='statement_expense_create'),
    path('statement_update/', StatementUpdateView.as_view(), name='statement_update'),
    path('statement_update/<int:pk>', StatementUpdateView.as_view(), name='statement_update'),
]