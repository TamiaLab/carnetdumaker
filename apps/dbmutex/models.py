"""
Data models for the database mutex apps.
"""

from datetime import timedelta

from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from .settings import MUTEX_LOCK_EXPIRATION_DELAY_SEC


class DbMutexLock(models.Model):
    """
    Data models of a mutex lock with a ``mutex_name`` and a ``creation_date``.
    The creation date only serve as a security to avoid dead lock.
    """

    mutex_name = models.CharField(_('Mutex name'),
                                  max_length=255,
                                  unique=True,
                                  db_index=True)  # Database optimization

    creation_date = models.DateTimeField(_('Creation date'),
                                         db_index=True,  # Database optimization
                                         auto_now_add=True)

    class Meta:
        verbose_name = _('Mutex lock')
        verbose_name_plural = _('Mutex locks')
        get_latest_by = 'creation_date'
        ordering = ('-creation_date', 'mutex_name')

    def __str__(self):
        return self.mutex_name

    def expired(self):
        """
        Return True if the mutex has expired, False otherwise.
        """
        if MUTEX_LOCK_EXPIRATION_DELAY_SEC is not None:
            expiration_threshold = timezone.now() - timedelta(seconds=MUTEX_LOCK_EXPIRATION_DELAY_SEC)
            return self.creation_date <= expiration_threshold
        else:
            return False
    expired.boolean = True
    expired.short_description = _('Mutex expired')
