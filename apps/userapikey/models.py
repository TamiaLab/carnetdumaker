"""
Data models for the user API keys app.
"""

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from .managers import UserApiKeyManager
from .settings import USER_API_KEY_TOKEN_GENERATOR


class UserApiKey(models.Model):
    """
    User API key data model.
    An user API key is made of:
    - an user (one-to-one relation),
    - an API key,
    - a last generation date.
    """

    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                related_name='api_key',
                                primary_key=True,
                                editable=False,
                                verbose_name=_('Related user'))

    api_key = models.CharField(_('API key'),
                               max_length=32,
                               db_index=True)

    last_generation_date = models.DateTimeField(_('Last generation date'),
                                                auto_now=True)

    objects = UserApiKeyManager()

    class Meta:
        verbose_name = _('User API key')
        verbose_name_plural = _('User API keys')
        get_latest_by = 'last_generation_date'
        ordering = ('-last_generation_date', )

    def __str__(self):
        return 'API key of "%s"' % self.user.username

    def is_token_valid(self, hash):
        """
        Return True if the given token/hash is valid for the current user and API key.
        :param hash: The token/hash to be checked.
        :return: True if the token is valid, False otherwise.
        """
        return USER_API_KEY_TOKEN_GENERATOR.check_token(self.user, self.api_key, hash)

    def get_full_api_key(self):
        """
        Get the full API key with user ID and token/hash signature.
        :return: The full API key, ready for use or display.
        """
        return USER_API_KEY_TOKEN_GENERATOR.make_token(self.user, self.api_key)
