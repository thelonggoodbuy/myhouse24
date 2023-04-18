from django.contrib import admin

from .models import Receipt, ReceiptCell



@admin.register(Receipt)
class UserAdmin(admin.ModelAdmin):
    list_display = ('number', 'appartment')
    list_filter = ('number', 'appartment')


@admin.register(ReceiptCell)
class UserAdmin(admin.ModelAdmin):
    list_display = ('receipt',)
    list_filter = ('receipt',)