from django.contrib import admin

from .models import Statement, PaymentItem


@admin.register(Statement)
class UserAdmin(admin.ModelAdmin):
    list_display = ('number', 'date', 'checked', 'type_of_paynent_item', 'personal_account')
    list_filter = ('number', )

@admin.register(PaymentItem)
class UserAdmin(admin.ModelAdmin):
    list_display = ('title', )
    list_filter = ('title', )