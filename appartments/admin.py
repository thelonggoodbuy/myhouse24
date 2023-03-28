from django.contrib import admin
from .models import House, HouseAdditionalImage, Section, Floor, Appartment, PersonalAccount


@admin.register(House)
class UserAdmin(admin.ModelAdmin):
    list_display = ('title', 'address')
    list_filter = ('title', 'address')


@admin.register(HouseAdditionalImage)
class UserAdmin(admin.ModelAdmin):
    list_display = ('house', 'image')
    list_filter = ('house', 'image')


@admin.register(Section)
class UserAdmin(admin.ModelAdmin):
    list_display = ('house', 'title')
    list_filter = ('house', 'title')

@admin.register(Floor)
class UserAdmin(admin.ModelAdmin):
    list_display = ('house', 'title')
    list_filter = ('house', 'title')


@admin.register(Appartment)
class UserAdmin(admin.ModelAdmin):
    list_display = ('house', 'number', 'personal_account')
    list_filter = ('house', )


@admin.register(PersonalAccount)
class UserAdmin(admin.ModelAdmin):
    list_display = ('number', 'status', 'balance')
    list_filter = ('number', )