"""
Data models for the licenses app.
"""

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from apps.tools.utils import unique_slug
from apps.txtrender.fields import RenderTextField
from apps.txtrender.utils import render_document
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
        content_html, content_text, _ = render_document(self.description,
                                                        allow_titles=True,
                                                        allow_alerts_box=True,
                                                        allow_text_formating=True,
                                                        allow_text_extra=True,
                                                        allow_text_alignments=True,
                                                        allow_text_directions=True,
                                                        allow_text_modifiers=True,
                                                        allow_text_colors=True,
                                                        allow_figures=True,
                                                        allow_lists=True,
                                                        allow_definition_lists=True,
                                                        allow_tables=True,
                                                        allow_quotes=True,
                                                        allow_footnotes=True,
                                                        allow_acronyms=True,
                                                        allow_links=True,
                                                        allow_medias=True,
                                                        allow_cdm_extra=True,
                                                        force_nofollow=False,
                                                        render_text_version=True,
                                                        merge_footnotes_html=True,
                                                        merge_footnotes_text=True)
        self.description_html = content_html
        self.description_text = content_text

        # Save if required
        if save:
            # Avoid infinite loop by calling directly super.save
            super(License, self).save(update_fields=('description_html', 'description_text'))


def _redo_licenses_text_rendering(sender, **kwargs):
    """
    Redo text rendering of all licenses.
    :param sender: Not used.
    :param kwargs: Not used.
    """
    for license in License.objects.all():
        license.render_description(save=True)


render_engine_changed.connect(_redo_licenses_text_rendering)
