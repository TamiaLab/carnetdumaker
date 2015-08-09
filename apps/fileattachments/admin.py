"""
Admin views for the file attachments app.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from .models import FileAttachment


class FileAttachmentAdmin(admin.ModelAdmin):
    """
    ``FileAttachment`` admin form.
    """

    list_display = ('filename',
                    'mimetype',
                    'upload_date',
                    'get_size_display',
                    'download_link',
                    'view_related_object')

    readonly_fields = ('upload_date',
                       'get_size_display',
                       'view_related_object')

    list_filter = ('upload_date',)

    search_fields = ('parent_post__id',
                     'content_type',
                     'filename')

    fieldsets = (
        (_('File'), {
            'fields': ('file',
                       'filename',
                       'mimetype')
        }),
        (_('Other stuff'), {
            'fields': ('get_size_display',
                       'upload_date')
        }),
        (_('Related object'), {
            'fields': ('view_related_object',)
        }),
    )

    def download_link(self, obj):
        """
        Simple "download file" inline callback.
        :param obj: Current database object.
        :return: HTML <a> link to the given object.
        """
        return format_html('<a href="{0}" class="link">{1}</a>',
                           obj.get_absolute_url(),
                           _('Download'))
    download_link.short_description = _('Download link')
    download_link.allow_tags = True

    def view_related_object(self, obj):
        """
        "View related object" inline callback.
        :param obj: Current database object.
        :return: HTML <a> link to the given object.
        """
        if not obj.content_object or not hasattr(obj.content_object, 'get_absolute_url'):
            return _('No link available')
        return format_html('<a href="{0}" class="link">{1}</a>',
                           obj.get_absolute_url(),
                           _('View related object'))
    view_related_object.short_description = _('View related object')
    view_related_object.allow_tags = True


admin.site.register(FileAttachment, FileAttachmentAdmin)
