"""
Utilities for the announcements app.
"""

from apps.twitter.utils import publish_link_on_twitter


def publish_announcement_on_twitter(announcement):
    """
    Publish the given announcement on Twitter.
    :param announcement: The announcement to be published.
    :return: The tweet ID on success, False on error.
    """
    return publish_link_on_twitter(announcement.title, announcement.get_absolute_url())
