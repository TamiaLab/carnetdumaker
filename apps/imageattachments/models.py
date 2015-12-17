"""
Data models for the image attachments app.
"""

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.core.files.uploadedfile import UploadedFile

from apps.licenses.models import License
from apps.tools.utils import unique_slug
from apps.tools.fields import ThumbnailImageField
from apps.txtrender.fields import RenderTextField
from apps.txtrender.utils import render_document
from apps.txtrender.signals import render_engine_changed

from .managers import ImageAttachmentManager
from .settings import (IMG_ATTACHMENT_UPLOAD_DIR_NAME,
                       IMG_ATTACHMENT_SMALL_THUMBNAIL_HEIGHT,
                       IMG_ATTACHMENT_SMALL_THUMBNAIL_WIDTH,
                       IMG_ATTACHMENT_MEDIUM_THUMBNAIL_HEIGHT,
                       IMG_ATTACHMENT_MEDIUM_THUMBNAIL_WIDTH,
                       IMG_ATTACHMENT_LARGE_THUMBNAIL_HEIGHT,
                       IMG_ATTACHMENT_LARGE_THUMBNAIL_WIDTH)


class ImageAttachment(models.Model):
    """
    Image attachment data model.
    An image attachment is made of:
    - a title (human readable),
    - a slug (unique and database indexed),
    - a published date (automatically set to current date and time),
    - a legend (optional),
    - a description (source and HTML version, optional),
    - a license (optional),
    - and an image with various thumbnails.

    Thumbnail's sizes are the same as with Wordpress:
    - small: 150x150px max (stored in dirname/small),
    - medium: 300x300px max (stored in dirname/medium),
    - large: 640x640px max (stored in dirname/large).
    Theses sizes can be changed in ``settings.py``.
    """

    title = models.CharField(_('Title'),
                             max_length=255)

    # FIXME AutoSlugField
    slug = models.SlugField(_('Slug'),
                            max_length=255,
                            unique=True)

    pub_date = models.DateTimeField(_('Publication date'),
                                    db_index=True,  # Database optimization
                                    auto_now_add=True)

    legend = models.CharField(_('Legend'),
                              max_length=255,
                              default='',
                              blank=True)

    description = RenderTextField(_('Description'),
                                   default='',
                                   blank=True)

    description_html = models.TextField(_('Description (raw HTML)'))

    description_text = models.TextField(_('Description (raw text)'))

    license = models.ForeignKey(License,
                                related_name='img_attachments',
                                verbose_name=_('License'),
                                default=None,
                                blank=True,
                                null=True)

    public_listing = models.BooleanField(_('Public listing'),
                                         default=True)

    img_small = ThumbnailImageField(_('Image (small size)'),
                                    upload_to=IMG_ATTACHMENT_UPLOAD_DIR_NAME + '/small',
                                    height_field='img_small_height',
                                    width_field='img_small_width',
                                    height=IMG_ATTACHMENT_SMALL_THUMBNAIL_HEIGHT,
                                    width=IMG_ATTACHMENT_SMALL_THUMBNAIL_WIDTH)
    img_small_height = models.IntegerField(_('Image height (small size, in pixels)'))
    img_small_width = models.IntegerField(_('Image width (small size, in pixels)'))

    img_medium = ThumbnailImageField(_('Image (medium size)'),
                                     upload_to=IMG_ATTACHMENT_UPLOAD_DIR_NAME + '/medium',
                                     height_field='img_medium_height',
                                     width_field='img_medium_width',
                                     height=IMG_ATTACHMENT_MEDIUM_THUMBNAIL_HEIGHT,
                                     width=IMG_ATTACHMENT_MEDIUM_THUMBNAIL_WIDTH)
    img_medium_height = models.IntegerField(_('Image height (medium size, in pixels)'))
    img_medium_width = models.IntegerField(_('Image width (medium size, in pixels)'))

    img_large = ThumbnailImageField(_('Image (large size)'),
                                    upload_to=IMG_ATTACHMENT_UPLOAD_DIR_NAME + '/large',
                                    height_field='img_large_height',
                                    width_field='img_large_width',
                                    height=IMG_ATTACHMENT_LARGE_THUMBNAIL_HEIGHT,
                                    width=IMG_ATTACHMENT_LARGE_THUMBNAIL_WIDTH)
    img_large_height = models.IntegerField(_('Image height (large size, in pixels)'))
    img_large_width = models.IntegerField(_('Image width (large size, in pixels)'))

    img_original = models.ImageField(_('Image (original size)'),
                                     upload_to=IMG_ATTACHMENT_UPLOAD_DIR_NAME,
                                     height_field='img_original_height',
                                     width_field='img_original_width')
    img_original_height = models.IntegerField(_('Image height (original size, in pixels)'))
    img_original_width = models.IntegerField(_('Image width (original size, in pixels)'))

    objects = ImageAttachmentManager()

    class Meta:
        verbose_name = _('Image attachment')
        verbose_name_plural = _('Image attachments')
        get_latest_by = 'pub_date'
        ordering = ('-pub_date', )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """
        Return the permalink to this image attachment.
        """
        return reverse('imageattachments:image_attachment_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        """
        Save the model
        :param args: For super()
        :param kwargs: For super()
        """

        # Avoid duplicate slug
        # FIXME AutoSlugField
        self.slug = unique_slug(ImageAttachment, self, self.slug, 'slug', self.title)

        # Render description text
        self.render_description()

        # Make the thumbnail versions
        self.make_thumbnails()

        # Save the attachment object
        super(ImageAttachment, self).save(*args, **kwargs)

    def make_thumbnails(self):
        """
        Make all thumbnails versions of the original image on upload.
        """
        if self.img_original and (isinstance(self.img_original.file, UploadedFile)
                                  or not self.img_small
                                  or not self.img_medium
                                  or not self.img_large):
            original_name = self.img_original.name
            if self.img_original.closed:
                self.img_original.open()
            original_content = self.img_original
            self.img_small.save(original_name, original_content, save=False)
            self.img_medium.save(original_name, original_content, save=False)
            self.img_large.save(original_name, original_content, save=False)

    def render_description(self, save=False):
        """
        Render the description. Save the model only if ``save`` is True.
        """

        # Render the description text
        content_html, content_text, _ = render_document(self.description,
                                                        allow_text_formating=True,
                                                        allow_text_extra=True,
                                                        allow_text_alignments=True,
                                                        allow_text_directions=True,
                                                        allow_text_modifiers=True,
                                                        allow_text_colors=True,
                                                        allow_spoilers=True,
                                                        allow_lists=True,
                                                        allow_tables=True,
                                                        allow_quotes=True,
                                                        allow_acronyms=True,
                                                        allow_links=True,
                                                        allow_medias=True,
                                                        allow_cdm_extra=True,
                                                        force_nofollow=False,
                                                        render_text_version=True)
        self.description_html = content_html
        self.description_text = content_text

        # Save if required
        if save:
            # Avoid infinite loop by calling directly super.save
            super(ImageAttachment, self).save(update_fields=('description_html', ))


def _redo_image_attachments_text_rendering(sender, **kwargs):
    """
    Redo text rendering of all image attachments.
    :param sender: Not used.
    :param kwargs: Not used.
    """
    for image in ImageAttachment.objects.all():
        image.render_description(save=True)

render_engine_changed.connect(_redo_image_attachments_text_rendering)
