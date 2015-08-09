"""
Data models for the force-logout app.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.signals import user_logged_in

from .managers import ForceLogoutOrderManager


FORCE_LOGOUT_SESSION_KEY = 'django_force_logout'


class ForceLogoutOrder(models.Model):
    """
    Server-side order to logout related user.
    Only one order can be assigned by user. At each authenticated requests, if the user last login date
    is before the ``order_date`` stored in this model, the user will be logged-out by the server.
    """

    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                related_name='+',
                                primary_key=True,
                                db_index=True,
                                editable=False,
                                verbose_name=_('Related user'))

    order_date = models.DateTimeField(_('Logout order date'))

    objects = ForceLogoutOrderManager()

    class Meta:
        verbose_name = _('Logout order')
        verbose_name_plural = _('Logout orders')
        get_latest_by = 'order_date'
        ordering = ('-order_date',)

    def __str__(self):
        return 'Logout order for "%s"' % self.user.username


def store_current_session_login_timestamp(sender, user, request, **kwargs):
    """
    Store the current time in the freshly connected user's session to avoid unwanted force logout.
    :param sender: Not used.
    :param user: Just logged in User instance.
    :param request: The current request object.
    :param kwargs: Not used.
    """
    request.session[FORCE_LOGOUT_SESSION_KEY] = timezone.now().timestamp()

user_logged_in.connect(store_current_session_login_timestamp)
