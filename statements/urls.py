from django.urls import path

from .views import StatementListView, StatementArrivalCreateView, StatementExpenseCreateView,\
                     StatementUpdateView, statemets_print_all, StatementDetailView, statemets_print_current_statment,\
                     StatementArrivalCopyView, StatementExpenseCopyView, ReceiptDeleteView,\
                     PaymentItemList, PaymentItemCreateView, PaymentItemUpdateView, PaymentItemDeleteView


app_name='statements'

urlpatterns = [
    path('statements_list/', StatementListView.as_view(), name='statements_list'),
    path('statement_arrival_create/', StatementArrivalCreateView.as_view(), name='statement_arrival_create'),
    path('statement_expense_create/', StatementExpenseCreateView.as_view(), name='statement_expense_create'),
    path('statement_update/', StatementUpdateView.as_view(), name='statement_update'),
    path('statement_update/<int:pk>', StatementUpdateView.as_view(), name='statement_update'),
    path('statement_detail/', StatementDetailView.as_view(), name="statement_detail"),
    path('statement_detail/<int:pk>', StatementDetailView.as_view(), name="statement_detail"),
    path('statement_arrival_copy/<int:pk>', StatementArrivalCopyView.as_view(), name="statement_arrival_copy"),
    path('statement_expense_copy/<int:pk>', StatementExpenseCopyView.as_view(), name="statement_expense_copy"),
    path('statemets_print_all/', statemets_print_all, name='statemets_print_all'),
    path('receipt_delete/<int:pk>', ReceiptDeleteView.as_view(), name="receipt_delete"),
    path('statemets_print_all/<int:pk>', statemets_print_current_statment, name="statemets_print_all"),



    path('payment_item_list/', PaymentItemList.as_view(), name='payment_item_list'),
    path('payment_item_new/', PaymentItemCreateView.as_view(), name='payment_item_new'),
    path('payment_item_update/', PaymentItemUpdateView.as_view(), name='payment_item_update'),
    path('payment_item_update/<int:pk>', PaymentItemUpdateView.as_view(), name='payment_item_update'),
    path('payment_item_delete/', PaymentItemDeleteView.as_view(), name='payment_item_delete'),
    path('payment_item_delete/<int:pk>', PaymentItemDeleteView.as_view(), name='payment_item_delete'),

]