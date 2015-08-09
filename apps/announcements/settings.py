"""
Custom settings for the announcements app.
"""

from django.conf import settings


# Number of announcements per page's widget
NB_ANNOUNCEMENTS_PER_PAGE_WIDGET = getattr(settings, 'NB_ANNOUNCEMENTS_PER_PAGE_WIDGET', 5)

# Number of announcements per page
NB_ANNOUNCEMENTS_PER_PAGE = getattr(settings, 'NB_ANNOUNCEMENTS_PER_PAGE', 25)

# Number of announcements per feed
NB_ANNOUNCEMENTS_PER_FEED = getattr(settings, 'NB_ANNOUNCEMENTS_PER_FEED', 10)
