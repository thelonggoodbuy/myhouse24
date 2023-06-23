from django.contrib import admin

from .models import Receipt, ReceiptCell\
                        # , ReceiptTemplate



@admin.register(Receipt)
class UserAdmin(admin.ModelAdmin):
    list_display = ('number', 'appartment')
    list_filter = ('number', 'appartment')


@admin.register(ReceiptCell)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'receipt')
    list_filter = ('receipt',)


# @admin.register(ReceiptTemplate)
# class UserAdmin(admin.ModelAdmin):
#     list_display = ('name', 'receipt_template', 'is_default')