"""
Data models for the user strike app.
"""

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from .managers import UserStrikeManager


class UserStrike(models.Model):
    """
    User strike model for administrators use only.
    An user strike contain:
    - an target user ID (can be null if IP address used),
    - an IP address (can be null if user ID used),
    - an expiration date,
    - a "block access" flag for ban,
    - an internal and public reason for the strike.
    """

    target_user = models.ForeignKey(settings.AUTH_USER_MODEL,
                                    db_index=True,  # Database optimization
                                    related_name='admin_strikes',
                                    verbose_name=_('Related user'),
                                    default=None,
                                    blank=True,
                                    null=True)

    target_ip_address = models.GenericIPAddressField(_('Related IP address'),
                                                     db_index=True,  # Database optimization
                                                     default=None,
                                                     blank=True,
                                                     null=True)

    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               db_index=True,  # Database optimization
                               related_name='authored_admin_strikes',
                               verbose_name=_('Author'))

    creation_date = models.DateTimeField(_('Creation date'),
                                         auto_now_add=True)

    expiration_date = models.DateTimeField(_('Expiration date'),
                                           default=None,
                                           blank=True,
                                           null=True)

    block_access = models.BooleanField(_('Block access (ban)'),
                                       default=False)

    internal_reason = models.TextField(_('Strike reason (internal)'))

    public_reason = models.TextField(_('Strike reason (public)'),
                                     default='',
                                     blank=True)

    objects = UserStrikeManager()

    class Meta:
        verbose_name = _('User strike')
        verbose_name_plural = _('User strikes')
        get_latest_by = 'creation_date'
        ordering = ('-creation_date', )

    def __str__(self):
        return 'Strike for "%s", reason: %s' % (self.target_user.username if self.target_user else self.target_ip_address,
                                                self.internal_reason)

    def clean(self):
        """
        Validate that the target user or the target ip address is set. The two fields can be set at the same time to
        provide an user ban with an IP ban.
        """
        if not self.target_user and not self.target_ip_address:
            raise ValidationError(_('You must select an user or enter an IP address.'),
                                  code='invalid_strike_target')
