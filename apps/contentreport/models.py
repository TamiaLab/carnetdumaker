"""
Models for the content report app.
"""

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from .managers import ContentReportManager


class ContentReport(models.Model):
    """
    User content report model.
    Use to store reporting of inadequate user content.
    A report is made of:
    - a related content (generic relation),
    - a reporter,
    - a report date,
    - and a reason (optional if obvious).
    """

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    reporter = models.ForeignKey(settings.AUTH_USER_MODEL,
                                 related_name='content_reports',
                                 editable=False,
                                 verbose_name=_('Reporter'))

    report_date = models.DateTimeField(_('Report date'),
                                       auto_now_add=True)

    reason = models.CharField(_('Reason'),
                              max_length=255,
                              default='',
                              blank=True)

    processed = models.BooleanField(_('Processed'),
                                    default=False)

    reporter_ip_address = models.GenericIPAddressField(_('Reporter IP address'),
                                                       default=None,
                                                       blank=True,
                                                       null=True)

    objects = ContentReportManager()

    class Meta:
        verbose_name = _('Content report')
        verbose_name_plural = _('Content reports')
        get_latest_by = 'report_date'
        ordering = ('-report_date',)

    def __str__(self):
        return 'Report from "%s", targeting: "%s" for reason: "%s"' % (self.reporter.username,
                                                                       self.content_object,
                                                                       self.reason)
