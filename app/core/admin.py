"""
Django admin customization.
"""

from core import models

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _


class UserAdmin(BaseUserAdmin):
    """ Defining the admin page for users """

    # Order users by id
    ordering = ['id']
    # Show the following fields in admin user section
    list_display = ['email', 'name']
    # Fieldsets to show in edit user page
    ''' Using _ for lazy translation to string (in another language) ,
        Translation will only happen when this string is
        used in code (future proofing) '''
    fieldsets = (
        (None, {'fields': ['email', 'name', 'password']}),
        (
            _('Permissions'),
            {
                'fields':
                [
                    'is_active',
                    'is_staff',
                    'is_superuser'
                ]
            }
        ),
        (_('Important Dates'), {'fields': ['last_login']}),
    )
    readonly_fields = ['last_login']
    add_fieldsets = (
        (
            None,
            {
                'classes': ['wide'],
                'fields': [
                    'email',
                    'password1',
                    'password2',
                    'name',
                    'is_active',
                    'is_staff',
                    'is_superuser',
                ]
            }
        ),
    )


# Register the user model and its admin configuration
admin.site.register(get_user_model(), UserAdmin)
admin.site.register(models.Recipe)
admin.site.register(models.Tag)
admin.site.register(models.Ingredient)
