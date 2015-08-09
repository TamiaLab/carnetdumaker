"""
Constants for the log watcher app.
"""

from django.utils.translation import ugettext_lazy as _


LOG_EVENT_LOGIN_SUCCESS = 0
LOG_EVENT_LOGIN_FAILED = 1
LOG_EVENT_LOGOUT = 2
LOG_EVENT_CHOICES = (
    (LOG_EVENT_LOGIN_SUCCESS, _('Login success')),
    (LOG_EVENT_LOGIN_FAILED, _('Login failed')),
    (LOG_EVENT_LOGOUT, _('Logout')),
)
