"""
Admin views for the content report app.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from .models import ContentReport


class ContentReportAdmin(admin.ModelAdmin):
    """
    Content report admin form.
    """

    list_select_related = ('reporter',)

    list_display = ('report_id',
                    'reporter_username_link',
                    'report_date',
                    'processed',
                    'reason',
                    'view_content_on_site')

    list_filter = ('report_date',
                   'processed')

    search_fields = ('id',
                     'reporter__email',
                     'reporter__username',
                     'reporter_ip_address',
                     'reason')

    readonly_fields = ('report_id',
                       'content_object',
                       'reporter_username_link',
                       'report_date',
                       'reporter_ip_address',
                       'reason',
                       'view_content_on_site')

    fieldsets = (
        (_('Report information'), {
            'fields': ('report_id',
                       'content_object',
                       'view_content_on_site',
                       'reporter_username_link',
                       'report_date',
                       'reason',
                       'reporter_ip_address')
        }),
        (_('Report management'), {
            'fields': ('processed',)
        }),
    )

    def report_id(self, obj):
        """
        Return the report ID in #ID format.
        :param obj: Current report object.
        :return: The report ID in #ID format.
        """
        return '#%d' % obj.id if obj.id else None
    report_id.short_description = _('ID')
    report_id.admin_order_field = 'id'

    def reporter_username_link(self, obj):
        """
        Return a link to the reporter.
        :param obj: Current ticket object.
        :return: HTML <a> link.
        """
        reporter = obj.reporter
        if reporter is None:
            return ''
        return format_html('<a href="{0}" class="link">{1}</a>',
                           reverse('admin:auth_user_change', args=[reporter.pk]),
                           reporter.username)
    reporter_username_link.short_description = _('Reporter')
    reporter_username_link.admin_order_field = 'reporter__username'
    reporter_username_link.allow_tags = True

    def view_content_on_site(self, obj):
        """
        Simple "view on site" inline callback.
        :param obj: Current database object.
        :return: HTML <a> link to the given object.
        """
        if not hasattr(obj, 'get_absolute_url'):
            return _('No link available')
        return format_html('<a href="{0}" class="link">{1}</a>',
                           obj.get_absolute_url(),
                           _('View on site'))
    view_content_on_site.short_description = _('View content on site')
    view_content_on_site.allow_tags = True


admin.site.register(ContentReport, ContentReportAdmin)
