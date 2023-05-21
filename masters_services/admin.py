from django.contrib import admin
from django.contrib import admin
from .models import MastersRequest


@admin.register(MastersRequest)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'description')
    # list_filter = ('title', 'address')
