from django.contrib import admin

from .models import UnitOfMeasure, UtilityService




@admin.register(UnitOfMeasure)
class UserAdmin(admin.ModelAdmin):
    list_display = ('title',)
    list_filter = ('title',)


@admin.register(UtilityService)
class UserAdmin(admin.ModelAdmin):
    list_display = ('title', 'unit_of_measure')
    list_filter = ('title', 'unit_of_measure')