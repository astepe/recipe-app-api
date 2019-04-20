from django.contrib import admin

# importing the default django user admin and change class variables to
# support custom user admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# recommended convention to converting strings to human-readable text
# gets passed through translation engine to support multiple
# languages
from django.utils.translation import gettext as _

from core import models


class UserAdmin(BaseUserAdmin):
    """change and create user admin page"""

    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('name',)}),
        (
            _('Permissions'),
            {'fields': ('is_active', 'is_staff', 'is_superuser')}
        ),
        (_('Important Dates'), {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')
        }),
    )


admin.site.register(models.User, UserAdmin)
