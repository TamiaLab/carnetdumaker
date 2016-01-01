"""
Custom settings for the forum app.
"""

from django.conf import settings


# Number of forum's threads per page (default 25)
NB_FORUM_THREAD_PER_PAGE = getattr(settings, 'NB_FORUM_THREAD_PER_PAGE', 25)

# Number of forum's posts per page (default 25)
NB_FORUM_POST_PER_PAGE = getattr(settings, 'NB_FORUM_POST_PER_PAGE', 25)

# Number of forum's threads per page widget (default 5)
NB_FORUM_THREAD_PER_PAGE_WIDGET = getattr(settings, 'NB_FORUM_THREAD_PER_PAGE_WIDGET', 5)

# Number of forum's posts per page widget (default 5)
NB_FORUM_POST_PER_PAGE_WIDGET = getattr(settings, 'NB_FORUM_POST_PER_PAGE_WIDGET', 5)

# Number of forum's threads in feeds
NB_FORUM_THREADS_IN_FEEDS = getattr(settings, 'NB_FORUM_THREADS_IN_FEEDS', 10)

# Number of forum's thread's posts in feeds
NB_FORUM_THREAD_POSTS_IN_FEEDS = getattr(settings, 'NB_FORUM_THREAD_POSTS_IN_FEEDS', 10)

# Number of forum's posts on the reply page (default 5)
NB_FORUM_POST_ON_REPLY_PAGE = getattr(settings, 'NB_FORUM_POST_ON_REPLY_PAGE', 5)

# Number of seconds between two post (anti flood, default 30s)
NB_SECONDS_BETWEEN_POSTS = getattr(settings, 'NB_SECONDS_BETWEEN_POSTS', 30)

# Height size of the forum's logo picture in pixels (default 120px)
FORUM_LOGO_HEIGHT_SIZE_PX = getattr(settings, 'FORUM_LOGO_HEIGHT_SIZE_PX', 120)

# Width size of the forum's logo picture in pixels (default 120px)
FORUM_LOGO_WIDTH_SIZE_PX = getattr(settings, 'FORUM_LOGO_WIDTH_SIZE_PX', 120)

# Forum's logo upload directory name
FORUM_LOGO_UPLOAD_DIR_NAME = getattr(settings, 'FORUM_LOGO_UPLOAD_DIR_NAME', 'forum_logo')

# Number of days before a logically deleted thread is really deleted.
DELETED_THREAD_PHYSICAL_DELETION_TIMEOUT_DAYS = getattr(settings, 'DELETED_THREAD_PHYSICAL_DELETION_TIMEOUT_DAYS', 365)

# Number of days before a logically deleted thread post is really deleted.
DELETED_THREAD_POST_PHYSICAL_DELETION_TIMEOUT_DAYS = getattr(settings,
                                                             'DELETED_THREAD_POST_PHYSICAL_DELETION_TIMEOUT_DAYS', 365)

# Number of days before a post become "old"
NB_DAYS_BEFORE_FORUM_POST_GET_OLD = getattr(settings, 'NB_DAYS_BEFORE_FORUM_POST_GET_OLD', 31 * 6)
