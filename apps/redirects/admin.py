"""
Admin models for the redirect app.
"""

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import Redirection


class RedirectionAdmin(admin.ModelAdmin):
    """
    Custom admin model for the ``Redirection`` model.
    """

    list_select_related = ('site', )

    list_display = ('site',
                    'old_path',
                    'new_path',
                    'permanent_redirect',
                    'active')

    list_filter = ('site',
                   'permanent_redirect',
                   'active')

    search_fields = ('site__domain',
                     'site__name',
                     'old_path',
                     'new_path')

    fieldsets = (
        (_('Site'), {
            'fields': ('site', )
        }),
        (_('URLs'), {
            'fields': ('old_path',
                       'new_path')
        }),
        (_('Metadata'), {
            'fields': ('permanent_redirect',
                       'active')
        }),
    )


admin.site.register(Redirection, RedirectionAdmin)
