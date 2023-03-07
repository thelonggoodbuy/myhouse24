from django.contrib import admin
from .models import User, Role


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'is_superuser', 'is_active', 'is_staff')
    list_filter = ('is_superuser', 'is_active')


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'id')
    list_filter = ('name', 'id')

# admin.site.register(User, UserAdmin)