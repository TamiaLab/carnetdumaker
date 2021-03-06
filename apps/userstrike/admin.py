"""
Admin models for the user strike app.
"""

from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from .models import UserStrike


class UserStrikeAdmin(admin.ModelAdmin):
    """
    Custom admin model for the ``UserStrike`` model.
    """

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        """
        Overload to pre-fill initial author with the current user PK.
        :param db_field: The current db field.
        :param request: The current request.
        :param kwargs: Extra named parameters.
        :return: super() result.
        """
        if db_field.name == 'author' and request is not None:
            kwargs['initial'] = request.user.id
        return super(UserStrikeAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    list_select_related = ('author', 'target_user')

    list_display = ('internal_reason',
                    'author_username_link',
                    'target_username_link',
                    'target_ip_address',
                    'creation_date',
                    'expiration_date',
                    'block_access')

    list_filter = ('creation_date',
                   'expiration_date',
                   'block_access')

    search_fields = ('author__email',
                     'author__username',
                     'target_user__email',
                     'target_user__username',
                     'target_ip_address',
                     'internal_reason',
                     'public_reason')

    raw_id_fields = ('author', 'target_user')

    readonly_fields = ('creation_date', )

    fieldsets = (
        (_('Target user'), {
            'fields': ('target_user',
                       'target_ip_address')
        }),
        (_('Metadata'), {
            'fields': ('author',
                       'block_access',
                       'creation_date',
                       'expiration_date')
        }),
        (_('Strike information'), {
            'fields': ('internal_reason',
                       'public_reason')
        }),
    )

    def author_username_link(self, obj):
        """
        Return the username of the related strike's author as a link to the related user admin edit page.
        :param obj: Current model object.
        """
        return '<a href="%s">%s</a>' % (reverse('admin:auth_user_change', args=[obj.author.pk]), obj.author.username)
    author_username_link.short_description = _('Author')
    author_username_link.admin_order_field = 'author__username'
    author_username_link.allow_tags = True

    def target_username_link(self, obj):
        """
        Return the username of the related user as a link to the related user admin edit page.
        :param obj: Current model object.
        """
        return '<a href="%s">%s</a>' % (reverse('admin:auth_user_change', args=[obj.target_user.pk]), obj.target_user.username)
    target_username_link.short_description = _('Related user')
    target_username_link.admin_order_field = 'target_user__username'
    target_username_link.allow_tags = True


admin.site.register(UserStrike, UserStrikeAdmin)
