from django.contrib import admin

from .models import UnitOfMeasure, UtilityService, Tariff, TariffCell, CounterReadings




@admin.register(UnitOfMeasure)
class UserAdmin(admin.ModelAdmin):
    list_display = ('title',)
    list_filter = ('title',)


@admin.register(UtilityService)
class UserAdmin(admin.ModelAdmin):
    list_display = ('title', 'unit_of_measure')
    list_filter = ('title', 'unit_of_measure')

# ----------------------------------------------------------------------------------
@admin.register(Tariff)
class UserAdmin(admin.ModelAdmin):
    list_display = ('title', 'updated_datetime')
    list_filter = ('title', 'updated_datetime')

@admin.register(TariffCell)
class UserAdmin(admin.ModelAdmin):
    list_display = ('tariff', 'number', 'updated_datetime', 'utility_service')
    list_filter = ('tariff', 'number', 'updated_datetime', 'utility_service')

# @admin.register(Counter)
# class UserAdmin(admin.ModelAdmin):
#     list_display = ('appartment',  )
#     list_filter = ('appartment', )


@admin.register(CounterReadings)
class UserAdmin(admin.ModelAdmin):
    list_display = ('utility_service', 'status', 'date', 'readings')
    list_filter = ('status', 'date')