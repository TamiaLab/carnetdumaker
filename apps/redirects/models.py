"""
Data models for the redirect app.
"""

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site

from .managers import RedirectionManager


class Redirection(models.Model):
    """
    A redirection data model used to store runtime redirection for old/obsolete URLS..
    A redirection is made of:
    - a site,
    - an old path (without the domain name),
    - a new path (can be blank to generate a "Gone" response),
    - a "permanent" flag,
    - an "active" flag.
    """

    site = models.ForeignKey(Site,
                             on_delete=models.CASCADE,
                             verbose_name=_('Site'))

    old_path = models.CharField(_('Old path'),
                                max_length=200,
                                db_index=True,
                                help_text=_("This should be an absolute path, excluding the domain name. "
                                            "Example: '/events/search/'."))

    new_path = models.CharField(_('New path'),
                                max_length=200,
                                blank=True,
                                default='',
                                help_text=_("This can be either an absolute path (as above) "
                                            "or a full URL starting with 'http://'. "
                                            "Can be blank if the redirection should raise a '410 Gone' response."))

    permanent_redirect = models.BooleanField(_('Permanent redirection'),
                                             default=True)

    active = models.BooleanField(_('Redirection enabled'),
                                 default=True)

    objects = RedirectionManager()

    class Meta:
        verbose_name = _('Redirect')
        verbose_name_plural = _('Redirects')
        unique_together = (('site', 'old_path'), )
        ordering = ('old_path', )

    def __str__(self):
        return "[%s] %s -> %s" % (self.site.domain, self.old_path, self.new_path)
