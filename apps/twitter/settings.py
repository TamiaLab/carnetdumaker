"""
Custom settings for the Twitter app.
"""

from django.conf import settings


# Consumer key (from https://apps.twitter.com/)
TWITTER_CONSUMER_KEY = getattr(settings, 'TWITTER_CONSUMER_KEY', None)

# Consumer secret (from https://apps.twitter.com/)
TWITTER_CONSUMER_SECRET = getattr(settings, 'TWITTER_CONSUMER_SECRET', None)

# OAuth token (from ``get_access_token.py`` helper of ``python-twitter``)
TWITTER_OAUTH_TOKEN = getattr(settings, 'TWITTER_OAUTH_TOKEN', None)

# OAuth token (from ``get_access_token.py`` helper of ``python-twitter``)
TWITTER_OAUTH_TOKEN_SECRET = getattr(settings, 'TWITTER_OAUTH_TOKEN_SECRET', None)

# Size of t.co links
TWITTER_LINKS_SIZE = getattr(settings, 'TWITTER_LINKS_SIZE', 25)

# Base URL for all links in tweets (with no trailing slash at end)
TWITTER_LINKS_BASE_URL = getattr(settings, 'TWITTER_LINKS_BASE_URL', 'http://127.0.0.1')
