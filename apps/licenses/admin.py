"""
Admin views for the licenses app.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from .models import License


class LicenseAdmin(admin.ModelAdmin):
    """
    Admin form for the ``License`` data model.
    """

    list_display = ('logo_img',
                    'name',
                    'view_on_site_link')

    list_display_links = ('logo_img',
                          'name')

    search_fields = ('name',
                     'description',
                     'usage',
                     'source_url')

    prepopulated_fields = {'slug': ('name', )}

    readonly_fields = ('logo_img',
                       'last_modification_date')

    fieldsets = (
        (_('Name and slug'), {
            'fields': ('name',
                       'slug')
        }),
        (_('Iconography'), {
            'fields': ('logo_img',
                       'logo')
        }),
        (_('License text'), {
            'fields': ('description',
                       'usage',
                       'source_url')
        }),
        (_('Date and time'), {
            'fields': ('last_modification_date',)
        }),
    )

    def logo_img(self, obj):
        """
        Return the current logo image as html ``<img>``.
        :param obj: Current model object.
        """
        return '<img src="%s" />' % obj.logo.url if obj.logo else ''
    logo_img.short_description = _('Logo')
    logo_img.allow_tags = True

    def view_on_site_link(self, obj):
        """
        Simple "view on site" inline callback.
        :param obj: Current database object.
        :return: HTML <a> link to the given object.
        """
        return format_html('<a href="{0}" class="link">{1}</a>',
                           obj.get_absolute_url(),
                           _('View on site'))
    view_on_site_link.short_description = ''
    view_on_site_link.allow_tags = True


admin.site.register(License, LicenseAdmin)
