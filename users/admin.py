from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'is_superuser', 'is_active', 'is_staff')
    list_filter = ('is_superuser', 'is_active')


# admin.site.register(User, UserAdmin)