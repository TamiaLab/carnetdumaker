"""
Admin views for the announcements app.
"""

from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from .models import Announcement


class AnnouncementAdmin(admin.ModelAdmin):
    """
    Admin panel for the ``Announcement`` model.
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
        return super(AnnouncementAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    list_select_related = ('author',)

    list_display = ('title',
                    'author_username_link',
                    'creation_date',
                    'last_content_modification_date',
                    'pub_date',
                    'type',
                    'site_wide',
                    'view_issue_on_site')

    list_filter = ('creation_date',
                   'last_content_modification_date',
                   'pub_date',
                   'type',
                   'site_wide')

    search_fields = ('title',
                     'author__username',
                     'author__email',
                     'content')

    raw_id_fields = ('author',)

    readonly_fields = ('author_username_link',
                       'view_issue_on_site',
                       'creation_date',
                       'last_content_modification_date')

    prepopulated_fields = {'slug': ('title',)}

    fieldsets = (
        (_('Title and slug'), {
            'fields': ('title',
                       'slug')
        }),
        (_('Content'), {
            'fields': ('author',
                       'type',
                       'site_wide',
                       'content')
        }),
        (_('Date and time'), {
            'fields': ('creation_date',
                       'pub_date',
                       'last_content_modification_date')
        }),
    )

    def author_username_link(self, obj):
        """
        Return the username of the related announcement's author as a link to the related user admin edit page.
        :param obj: Current model object.
        """
        return '<a href="%s">%s</a>' % (reverse('admin:auth_user_change', args=[obj.author.pk]), obj.author.username)
    author_username_link.short_description = _('Author')
    author_username_link.admin_order_field = 'author__username'
    author_username_link.allow_tags = True

    def view_issue_on_site(self, obj):
        """
        Simple "view on site" inline callback.
        :param obj: Current database object.
        :return: HTML <a> link to the given object.
        """
        return format_html('<a href="{0}" class="link">{1}</a>',
                           obj.get_absolute_url(),
                           _('View on site'))
    view_issue_on_site.short_description = ''
    view_issue_on_site.allow_tags = True


admin.site.register(Announcement, AnnouncementAdmin)
