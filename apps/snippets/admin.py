"""
Admin models for the code snippets app.
"""

from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from .models import CodeSnippet


class CodeSnippetAdmin(admin.ModelAdmin):
    """
    Custom admin model for the ``CodeSnippet`` model.
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
        return super(CodeSnippetAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    list_select_related = ('author',)

    list_display = ('filename',
                    'title',
                    'author_username_link',
                    'code_language',
                    'creation_date',
                    'last_modification_date',
                    'view_issue_on_site')

    list_display_links = ('filename',
                          'title')

    list_filter = ('creation_date',
                   'last_modification_date',
                   'display_line_numbers')

    search_fields = ('author__email',
                     'author__username',
                     'filename',
                     'title',
                     'code_language',
                     'source_code')

    raw_id_fields = ('author',)

    readonly_fields = ('creation_date',
                       'last_modification_date')

    fieldsets = (
        (_('Title'), {
            'fields': ('title',)
        }),
        (_('Metadata'), {
            'fields': ('author',
                       'filename',
                       'code_language',
                       'public_listing',
                       'creation_date',
                       'last_modification_date')
        }),
        (_('Source code'), {
            'fields': ('description',
                       'source_code')
        }),
        (_('Display options'), {
            'fields': ('display_line_numbers',
                       'highlight_lines',
                       'tab_size')
        }),
    )

    def author_username_link(self, obj):
        """
        Return the username of the related code snippet's author as a link to the related user admin edit page.
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


admin.site.register(CodeSnippet, CodeSnippetAdmin)
