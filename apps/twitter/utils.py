"""
Utilities for the Twitter app.
"""

import tweepy

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .settings import (TWITTER_CONSUMER_KEY,
                       TWITTER_CONSUMER_SECRET,
                       TWITTER_OAUTH_TOKEN,
                       TWITTER_OAUTH_TOKEN_SECRET,
                       TWITTER_LINKS_SIZE,
                       TWITTER_LINKS_BASE_URL)


# Load the Twitter API
if TWITTER_CONSUMER_KEY and TWITTER_CONSUMER_SECRET and TWITTER_OAUTH_TOKEN and TWITTER_OAUTH_TOKEN_SECRET:
    _auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
    _auth.secure = True
    _auth.set_access_token(TWITTER_OAUTH_TOKEN, TWITTER_OAUTH_TOKEN_SECRET)
    twitter_api = tweepy.API(_auth)

elif not settings.DEBUG:
    raise ImproperlyConfigured('Twitter consumer key/secret and/or OAuth token/secret not set!')


def publish_link_on_twitter(text, url):
    """
    Publish the given link on Twitter with the given text as label.
    :param text: The text to be published.
    :param url: The link URL to be published.
    :return: The tweet ID on success, False on error.
    """

    # Do not send anything in debug mode, just fake it
    if settings.DEBUG:
        import random
        return str(random.getrandbits(64))

    # Crop the text if necessary
    if len(text) > 140 - TWITTER_LINKS_SIZE - 1:
        text = text[:140 - TWITTER_LINKS_SIZE - 2]
        text += '\u2026'

    # Add the link
    message = text + ' ' + TWITTER_LINKS_BASE_URL + url

    # Post the message
    try:
        status = twitter_api.update_status(message)
    except tweepy.TweepError:
        return False

    # Return the tweet ID
    return str(status.id)
