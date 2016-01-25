"""
Admin models for the user API keys app.
"""

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import UserApiKey


class UserApiKeyAdmin(admin.ModelAdmin):
    """
    Custom admin model for the ``UserApiKey`` model.
    """

    list_select_related = ('user', )

    list_display = ('user', 'last_generation_date')

    list_filter = ('last_generation_date', )

    search_fields = ('user__email',
                     'user__username',
                     'api_key')

    raw_id_fields = ('user', )

    readonly_fields = ('user',
                       'last_generation_date')

    fieldsets = (
        (_('Metadata'), {
            'fields': ('user',
                       'api_key',
                       'last_generation_date')
        }),
    )


admin.site.register(UserApiKey, UserApiKeyAdmin)
