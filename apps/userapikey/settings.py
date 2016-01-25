"""
Custom settings for the user API key app.
"""

from django.conf import settings
from django.conf import ImproperlyConfigured
from django.utils.module_loading import import_string


# Token generator class path
USER_API_KEY_TOKEN_GENERATOR = getattr(settings, 'USER_API_KEY_TOKEN_GENERATOR',
                                       'apps.userapikey.tokens.default_token_generator')

# Import the class
try:
    USER_API_KEY_TOKEN_GENERATOR = import_string(USER_API_KEY_TOKEN_GENERATOR)
except ImportError:
    raise ImproperlyConfigured('Cannot import the class for the USER_API_KEY_TOKEN_GENERATOR setting (required).')
