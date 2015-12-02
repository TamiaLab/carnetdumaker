"""
Development Django settings for the CarnetDuMaker project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/

For the full list of common settings and their values, see
`carnetdumaker.settings.common.py`
"""

from .common import *

#region ----- Core settings

# Set to true to enable project debug mode
# SECURITY WARNING: don't run with debug turned on in production!
# See https://docs.djangoproject.com/en/1.7/ref/settings/#debug
DEBUG = True

# Set to true to enable template debug mode
# See https://docs.djangoproject.com/en/1.7/ref/settings/#template-debug
TEMPLATES[0]['OPTIONS']['debug'] = True

# List of accepted Host header values, must be synced with the web server configuration
# See https://docs.djangoproject.com/en/1.7/ref/settings/#allowed-hosts
ALLOWED_HOSTS = [
    'www.carnetdumaker.dev'
]

# List of supported password hashers, Weak SHA1 hashers first in dev for fast unit-testing.
# See https://docs.djangoproject.com/en/1.7/ref/settings/#password-hashers
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
)

#endregion

#region ----- Cache settings

# Cache backend options
# See https://docs.djangoproject.com/en/1.7/ref/settings/#caches
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'somewhere',
        'KEY_PREFIX': CACHE_KEY_PREFIX,
    }
}

#endregion

#region ----- Email settings

# Email backend for sending email
# See https://docs.djangoproject.com/en/1.7/ref/settings/#std:setting-EMAIL_BACKEND
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Fake email to be used with the console email backend
ADMINS = [
    ('John doe', 'john.doe@localhost'),
]
MANAGERS = ADMINS

#endregion

#region ----- Sessions settings

# Set to true to force client browser to sent the session cookies over HTTPS
# See https://docs.djangoproject.com/en/1.7/ref/settings/#session-cookie-secure
SESSION_COOKIE_SECURE = False

#endregion

#region ----- CSRF settings

# Set to true to force client browser to sent the cookies over HTTPS
# See https://docs.djangoproject.com/en/1.7/ref/settings/#csrf-cookie-secure
CSRF_COOKIE_SECURE = False

#endregion

#region ----- Debug toolbar

# Load django-debug-toolbar in debug mode
if DEBUG:
    import debug_toolbar
    INSTALLED_APPS.append('debug_toolbar')
    INTERNAL_IPS = ['127.0.0.1', '10.0.2.2']
    MIDDLEWARE_CLASSES.insert(
        MIDDLEWARE_CLASSES.index('django.middleware.common.CommonMiddleware') + 1,
        'debug_toolbar.middleware.DebugToolbarMiddleware')

#endregion

# Haystack settings
#HAYSTACK_SEARCH_ENGINE = 'whoosh'
