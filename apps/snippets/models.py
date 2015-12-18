"""
Data models for the code snippets app.
"""

from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.styles import get_style_by_name

from apps.tools.models import ModelDiffMixin
from apps.txtrender.fields import RenderTextField
from apps.txtrender.utils import render_document
from apps.txtrender.signals import render_engine_changed

from .settings import (SNIPPETS_DEFAULT_TABULATION_SIZE,
                       SNIPPETS_DISPLAY_LINE_NUMBERS_BY_DEFAULT,
                       SNIPPETS_PYGMENTS_CSS_STYLE_NAME,
                       SNIPPETS_PYGMENTS_CSS_NAMESPACE)
from .constants import (CODE_LANGUAGE_CHOICES,
                        CODE_LANGUAGE_DEFAULT)
from .managers import CodeSnippetManager


class CodeSnippet(ModelDiffMixin, models.Model):
    """
    Data model for a code snippet.
    A code snippet is made of:
    - an id,
    - a title,
    - a author,
    - a file name,
    - a code language (for highlighting),
    - a description
    - some source code (plain text),
    - the HTML version of the source code + CSS classes (for display),
    - some Pygments specific options,
    - a creation and last modification date for SEO.
    """

    title = models.CharField(_('Title'),
                             max_length=255)

    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               db_index=True,  # Database optimization
                               related_name='snippets',
                               verbose_name=_('Author'))

    filename = models.CharField(_('Filename'),
                                max_length=255)

    code_language = models.CharField(_('Code language'),
                                     choices=CODE_LANGUAGE_CHOICES,
                                     default=CODE_LANGUAGE_DEFAULT,
                                     max_length=255,
                                     blank=False)

    public_listing = models.BooleanField(_('Public listing'),
                                         default=True)

    # TODO Add license field (FK) with according admin forms, views, feeds

    description = RenderTextField(_('Description'))

    description_html = models.TextField(_('Description (raw HTML)'))

    description_text = models.TextField(_('Description (raw text)'))

    source_code = models.TextField(_('Source code'))

    html_for_display = models.TextField(_('HTML for display'),
                                        editable=False,
                                        blank=True)

    css_for_display = models.TextField(_('CSS for display'),
                                       editable=False,
                                       blank=True)

    display_line_numbers = models.BooleanField(_('Display line numbers'),
                                               default=SNIPPETS_DISPLAY_LINE_NUMBERS_BY_DEFAULT)

    highlight_lines = models.CommaSeparatedIntegerField(_('Highlight lines'),
                                                        help_text=_('Enter line numbers separated by comma.'),
                                                        max_length=255,
                                                        default='',
                                                        blank=True)

    tab_size = models.PositiveSmallIntegerField(_('Tabulation size in space'),
                                                default=SNIPPETS_DEFAULT_TABULATION_SIZE)

    creation_date = models.DateTimeField(_('Creation date'),
                                         auto_now_add=True)

    last_modification_date = models.DateTimeField(_('Last modification date'),
                                                  default=None,
                                                  editable=False,
                                                  null=True,
                                                  blank=True)

    objects = CodeSnippetManager()

    class Meta:
        verbose_name = _('Code snippet')
        verbose_name_plural = _('Code snippets')
        get_latest_by = 'creation_date'
        ordering = ('-creation_date', )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """
        Returns the permalink to this snippet.
        """
        return reverse('snippets:snippet_detail', kwargs={'pk': self.pk})

    def get_download_url(self):
        """
        Returns the download link to this snippet.
        """
        return reverse('snippets:snippet_download', kwargs={'pk': self.pk})

    def get_raw_url(self):
        """
        Returns the "see raw" link to this snippet.
        """
        return reverse('snippets:snippet_raw', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        """
        Save the model, also render the HTML version of the source code.
        :param args: For super()
        :param kwargs: For super()
        :return: None
        """

        # Render description
        self.render_description()

        # Fix last modification date if necessary
        changed_fields = self.changed_fields
        if self.pk and ('title' in changed_fields or
                                'filename' in changed_fields or
                                'description' in changed_fields or
                                'source_code' in changed_fields):
            self.last_modification_date = timezone.now()

        # Render the HTML version of the source code
        lexer = get_lexer_by_name(self.code_language,
                                  stripall=True,
                                  tabsize=self.tab_size)
        style = get_style_by_name(SNIPPETS_PYGMENTS_CSS_STYLE_NAME)
        formatter = HtmlFormatter(style=style,
                                  linenos='table' if self.display_line_numbers else False,
                                  hl_lines=self.get_highlight_lines(),
                                  cssclass=SNIPPETS_PYGMENTS_CSS_NAMESPACE,
                                  anchorlinenos=True,
                                  lineanchors='line')
        self.html_for_display = highlight(self.source_code, lexer, formatter)
        self.css_for_display = formatter.get_style_defs()

        # Save the model
        super(CodeSnippet, self).save(*args, **kwargs)

    def has_been_modified(self):
        """
        Return True if the snippet has been modified after creation.
        """
        return self.last_modification_date is not None \
               and self.last_modification_date != self.creation_date

    def get_highlight_lines(self):
        """
        Return ``highlight_lines`` as a list of int.
        """
        if not self.highlight_lines:
            return []
        return [int(i) for i in self.highlight_lines.split(',')]

    def render_description(self, save=False):
        """
        Render the description.
        :param save: Save the model field ``content_html`` if ``True``.
        """

        # Render HTML
        content_html, content_text, _ = render_document(self.content,
                                                        allow_text_formating=True,
                                                        allow_text_extra=True,
                                                        allow_text_alignments=True,
                                                        allow_text_directions=True,
                                                        allow_text_modifiers=True,
                                                        allow_text_colors=True,
                                                        allow_spoilers=True,
                                                        allow_lists=True,
                                                        allow_definition_lists=True,
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
            self.save_no_rendering(update_fields=('description_html', 'description_text'))


def _redo_code_snippets_text_rendering(sender, **kwargs):
    """
    Redo text rendering of all code snippets.
    :param sender: Not used.
    :param kwargs: Not used.
    """
    for snippet in CodeSnippet.objects.all():
        snippet.render_description(save=True)

render_engine_changed.connect(_redo_code_snippets_text_rendering)
