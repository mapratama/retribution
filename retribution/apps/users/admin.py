from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


class UserAdmin(DjangoUserAdmin):
    #  for edit
    fieldsets = (
        (None, {'fields': ('username', 'name', 'mobile_number',
                           'password', 'destinations')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('date_joined',)}),
    )
    # for add
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2')}
        ),
    )
    list_display = ('username', 'email', 'name', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active',)
    search_fields = ('username', 'name', 'email')
    ordering = ('username',)

admin.site.register(User, UserAdmin)
