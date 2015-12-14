"""
Data models for the log watcher app.
"""

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.signals import (user_logged_in,
                                         user_login_failed,
                                         user_logged_out)

from apps.tools.http_utils import get_client_ip_address

from .constants import (LOG_EVENT_CHOICES,
                        LOG_EVENT_LOGIN_SUCCESS,
                        LOG_EVENT_LOGIN_FAILED,
                        LOG_EVENT_LOGOUT)


class LogEvent(models.Model):
    """
    A log event data model.
    A log event is made of:
    - a event type (LOGIN_SUCCESS, LOGIN_FAILED, LOGOUT),
    - a event timestamp,
    - an username,
    - an IP address.
    """

    type = models.PositiveSmallIntegerField(_('Event'),
                                            db_index=True,  # Database optimization
                                            editable=False,
                                            choices=LOG_EVENT_CHOICES)

    event_date = models.DateTimeField(_('Date'),
                                      db_index=True,  # Database optimization
                                      auto_now=True)

    username = models.CharField(_('Username'),
                                db_index=True,  # Database optimization
                                editable=False,
                                max_length=255)

    ip_address = models.GenericIPAddressField(_('IP address'),
                                              db_index=True,  # Database optimization
                                              editable=False,
                                              blank=True,
                                              null=True)

    class Meta:
        verbose_name = _('Log event')
        verbose_name_plural = _('Log events')
        get_latest_by = 'event_date'
        ordering = ('-event_date', )

    def __str__(self):
        type_map = {
            LOG_EVENT_LOGIN_SUCCESS: 'LOGIN_SUCCESS',
            LOG_EVENT_LOGIN_FAILED: 'LOGIN_FAILED',
            LOG_EVENT_LOGOUT: 'LOGOUT',
        }
        return "[%s] %s %s from %s" % (self.event_date.isoformat(' '),
                                       type_map[self.type],
                                       self.username, self.ip_address)


def _handle_user_login_success(sender, request, user, **kwargs):
    """
    Handle user login in.
    :param sender: The sender class.
    :param request: The current request.
    :param user: The logged-in user.
    :param kwargs: Extra keywords arguments.
    :return: None
    """

    # Log the event
    LogEvent.objects.create(type=LOG_EVENT_LOGIN_SUCCESS,
                            username=user.username,
                            ip_address=get_client_ip_address(request))


user_logged_in.connect(_handle_user_login_success)


def _handle_user_login_failed(sender, credentials, **kwargs):
    """
    Handle failed login attempt.
    We cannot log the attacker IP address from this signal because the
    ``authenticate()`` method from the ``contrib.auth`` package is broken by design.
    See https://code.djangoproject.com/ticket/23155 for details.
    This signal remain useful because we can keep monitor failed attempt on a specific account.
    :param sender: The sender class.
    :param credentials: Credentials passed to the ``authenticate()`` method.
    :param kwargs: Extra keywords arguments.
    :return: None
    """

    # Log the event
    LogEvent.objects.create(type=LOG_EVENT_LOGIN_FAILED,
                            username=credentials['username'],
                            ip_address=None)


user_login_failed.connect(_handle_user_login_failed)


def _handle_user_logout(sender, request, user, **kwargs):
    """
    Handle user logout.
    :param sender: The sender class.
    :param request: The current request.
    :param user: The logged-out user.
    :param kwargs: Extra keywords arguments.
    :return: None
    """

    # Do nothing if the user was not logged-in
    if user is None:
        return

    # Log the event
    LogEvent.objects.create(type=LOG_EVENT_LOGOUT,
                            username=user.username,
                            ip_address=get_client_ip_address(request))


user_logged_out.connect(_handle_user_logout)
