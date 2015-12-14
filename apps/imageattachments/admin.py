"""
Admin views for the image attachments app.
"""

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.utils.html import format_html
from django.template import loader

from .models import ImageAttachment


class ImageAttachmentAdmin(admin.ModelAdmin):
    """
    Admin form for the ``ImageAttachment`` data model.
    """

    integration_code_template_name = 'imageattachments/admin_img_integration_code.html'

    list_display = ('small_img',
                    'title',
                    'pub_date',
                    'legend',
                    'public_listing',
                    'view_on_site')

    list_display_links = ('small_img',
                          'title')

    search_fields = ('title',
                     'slug',
                     'legend'
                     'description',
                     'img_original')

    list_filter = ('pub_date',
                   'public_listing')

    readonly_fields = ('pub_date',
                       'img_original_height',
                       'img_original_width',
                       'img_original_int_code',
                       'img_small',
                       'img_small_height',
                       'img_small_width',
                       'img_small_int_code',
                       'img_medium',
                       'img_medium_height',
                       'img_medium_width',
                       'img_medium_int_code',
                       'img_large',
                       'img_large_height',
                       'img_large_width',
                       'img_large_int_code')

    prepopulated_fields = {'slug': ('title', )}

    fieldsets = (
        (_('Title and slug'), {
            'fields': ('title',
                       'slug',
                       'public_listing')
        }),
        (_('Legend, description and license'), {
            'fields': ('legend',
                       'description',
                       'license')
        }),
        (_('Image (original)'), {
            'fields': ('img_original',
                       'img_original_int_code')
        }),
        (_('Image (small thumbnail)'), {
            'fields': ('img_small',
                       'img_small_int_code')
        }),
        (_('Image (medium thumbnail)'), {
            'fields': ('img_medium',
                       'img_medium_int_code')
        }),
        (_('Image (large thumbnail)'), {
            'fields': ('img_large',
                       'img_large_int_code')
        }),
        (_('Date and time'), {
            'fields': ('pub_date', )
        }),
    )

    def small_img(self, obj):
        """
        Return the current small thumbnail image as html ``<img>``.
        :param obj: Current model object.
        """
        return '<img src="%s" />' % obj.img_small.url if obj.img_small else ''
    small_img.short_description = _('Image')
    small_img.allow_tags = True

    def view_on_site(self, obj):
        """
        Simple "view on site" inline callback.
        :param obj: Current database object.
        :return: HTML <a> link to the given object.
        """
        return format_html('<a href="{0}" class="link">{1}</a>',
                           obj.get_absolute_url(),
                           _('View on site'))
    view_on_site.short_description = ''
    view_on_site.allow_tags = True

    def img_int_code(self, obj, img, height, width):
        """
        Helper to generated image integration code.
        :param obj: Current model object.
        :param img: The image field instance.
        :param height: The image height field instance.
        :param width: The image width field instance.
        """
        context = {
            'obj': obj,
            'img': img,
            'height': height,
            'width': width
        }
        return loader.render_to_string(self.integration_code_template_name, context)

    def img_small_int_code(self, obj):
        """
        Return the current small thumbnail image as html ``<img>``.
        :param obj: Current model object.
        """
        return self.img_int_code(obj, obj.img_small,
                                 obj.img_small_height, obj.img_small_width) if obj.img_small else ''
    img_small_int_code.short_description = _('HTML integration code')
    img_small_int_code.allow_tags = True

    def img_medium_int_code(self, obj):
        """
        Return the current medium thumbnail image as html ``<img>``.
        :param obj: Current model object.
        """
        return self.img_int_code(obj, obj.img_medium,
                                 obj.img_medium_height, obj.img_medium_width) if obj.img_medium else ''
    img_medium_int_code.short_description = _('HTML integration code')
    img_medium_int_code.allow_tags = True

    def img_large_int_code(self, obj):
        """
        Return the current large thumbnail image as html ``<img>``.
        :param obj: Current model object.
        """
        return self.img_int_code(obj, obj.img_large,
                                 obj.img_large_height, obj.img_large_width) if obj.img_large else ''
    img_large_int_code.short_description = _('HTML integration code')
    img_large_int_code.allow_tags = True

    def img_original_int_code(self, obj):
        """
        Return the current large thumbnail image as html ``<img>``.
        :param obj: Current model object.
        """
        return self.img_int_code(obj, obj.img_original,
                                 obj.img_original_height, obj.img_original_width) if obj.img_original else ''
    img_original_int_code.short_description = _('HTML integration code')
    img_original_int_code.allow_tags = True


admin.site.register(ImageAttachment, ImageAttachmentAdmin)
