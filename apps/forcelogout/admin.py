"""
Admin views for the force-logout app.
"""

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import ForceLogoutOrder


class ForceLogoutOrderAdmin(admin.ModelAdmin):
    """
    Admin page for the ``ForceLogoutOrder`` model.
    """

    list_select_related = ('user',)

    list_display = ('user_username',
                    'order_date')

    list_filter = ('order_date',)

    search_fields = ('user__email',
                     'user__username')

    readonly_fields = ('user',)

    fieldsets = (
        (_('Logout order'), {
            'fields': ('user',
                       'order_date')
        }),
    )

    raw_id_fields = ('user',)

    def user_username(self, obj):
        """
        Return the username of the related user.
        :param obj: Current model object.
        """
        return obj.user.username
    user_username.short_description = _('Username')
    user_username.admin_order_field = 'user__username'


admin.site.register(ForceLogoutOrder, ForceLogoutOrderAdmin)
