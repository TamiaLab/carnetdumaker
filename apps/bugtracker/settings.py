"""
Custom settings for the bug tracker app.
"""

from django.conf import settings


# Number of issue in the "recent issues" feed
NB_ISSUES_IN_RECENT_ISSUE_FEED = getattr(settings, 'NB_ISSUES_IN_RECENT_ISSUE_FEED', 10)

# Number of comment in the "recent comments" feed
NB_COMMENTS_IN_RECENT_COMMENT_FEED = getattr(settings, 'NB_COMMENTS_IN_RECENT_COMMENT_FEED', 10)

# Number of issue per page (default 25)
NB_ISSUES_PER_PAGE = getattr(settings, 'NB_ISSUES_PER_PAGE', 25)

# Number of issue's comments per page (default 25)
NB_ISSUE_COMMENTS_PER_PAGE = getattr(settings, 'NB_ISSUE_COMMENTS_PER_PAGE', 25)

# Minimum number of seconds between two consecutive comments
NB_SECONDS_BETWEEN_COMMENTS = getattr(settings, 'NB_SECONDS_BETWEEN_COMMENTS', 30)
