"""
Data models for the licenses app.
"""

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from apps.tools.utils import unique_slug
from apps.txtrender.fields import RenderTextField
from apps.txtrender.utils import render_html, strip_html
from apps.txtrender.signals import render_engine_changed

from .settings import LICENSE_LOGO_UPLOAD_DIR_NAME


class License(models.Model):
    """
    Content license data model.
    A license is made of:
    - a name (human readable),
    - a slug (unique and indexed in database),
    - an optional logo (only full size version),
    - a brief description (can be blank),
    - a full usage text (can be blank),
    - an optional source URL (for external license like CC).
    """

    name = models.CharField(_('Name'),
                            db_index=True,
                            max_length=255)

    # FIXME AutoSlugField
    slug = models.SlugField(_('Slug'),
                            max_length=255,
                            unique=True)

    logo = models.ImageField(_('Logo'),
                             upload_to=LICENSE_LOGO_UPLOAD_DIR_NAME,
                             default=None,
                             blank=True,
                             null=True)

    description = RenderTextField(_('Description'))

    description_html = models.TextField(_('Description (raw HTML)'))

    description_text = models.TextField(_('Description (raw text)'))

    usage = models.TextField(_('Usage'),
                             default='',
                             blank=True)

    source_url = models.URLField(_('Source URL'),
                                 default='',
                                 blank=True)

    last_modification_date = models.DateTimeField(_('Last modification date'),
                                                  auto_now=True)

    class Meta:
        verbose_name = _('License')
        verbose_name_plural = _('Licenses')
        ordering = ('name', )
        # FIXME Permissions for skcode

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """
        Return the permalink to this license.
        """
        return reverse('licenses:license_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        """
        Save the license.
        :param args: For super()
        :param kwargs: For super()
        """

        # Avoid duplicate slug
        # FIXME AutoSlugField
        self.slug = unique_slug(License, self, self.slug, 'slug', self.name)

        # Render the description text
        self.render_description()

        # Save the license
        super(License, self).save(*args, **kwargs)

    def render_description(self, save=False):
        """
        Render the description. Save the model only if ``save`` is True.
        """

        # Render HTML
        # FIXME Deploy skcode engine
        self.description_html = render_html(self.description, force_nofollow=False)
        self.description_text = 'TODO'

        # Save if required
        if save:
            # Avoid infinite loop by calling directly super.save
            super(License, self).save(update_fields=('description_html',))


def _redo_licenses_text_rendering(sender, **kwargs):
    """
    Redo text rendering of all licenses.
    :param sender: Not used.
    :param kwargs: Not used.
    """
    for license in License.objects.all():
        license.render_description(save=True)


render_engine_changed.connect(_redo_licenses_text_rendering)
