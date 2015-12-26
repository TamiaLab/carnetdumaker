"""
Custom settings for the blog app.
"""

from django.conf import settings


# Height in pixels of the article's heading image
ARTICLE_HEADING_IMG_HEIGHT = getattr(settings, 'ARTICLE_HEADING_IMG_HEIGHT', 300)

# Width in pixels of the article's heading image
ARTICLE_HEADING_IMG_WIDTH = getattr(settings, 'ARTICLE_HEADING_IMG_WIDTH', 900)

# Upload directory name for article's heading images.
ARTICLE_HEADING_UPLOAD_DIR_NAME = getattr(settings, 'ARTICLE_HEADING_UPLOAD_DIR_NAME', 'headings/')

# Height in pixels of the article's thumbnail image
ARTICLE_THUMBNAIL_IMG_HEIGHT = getattr(settings, 'ARTICLE_THUMBNAIL_IMG_HEIGHT', 180)

# Width in pixels of the article's thumbnail image
ARTICLE_THUMBNAIL_IMG_WIDTH = getattr(settings, 'ARTICLE_THUMBNAIL_IMG_WIDTH', 260)

# Upload directory name for article's thumbnail images.
ARTICLE_THUMBNAIL_UPLOAD_DIR_NAME = getattr(settings, 'ARTICLE_THUMBNAIL_UPLOAD_DIR_NAME', 'headings_thumbnail/')

# Number of articles per page
NB_ARTICLES_PER_PAGE = getattr(settings, 'NB_ARTICLES_PER_PAGE', 25)

# Number of articles per page widget
NB_ARTICLES_PER_PAGE_WIDGET = getattr(settings, 'NB_ARTICLES_PER_PAGE_WIDGET', 5)

# Parent forum ID for all article related forum's thread (None = no related thread created).
PARENT_FORUM_ID_FOR_ARTICLE_THREADS = getattr(settings, 'PARENT_FORUM_ID_FOR_ARTICLE_THREADS', None)

# Number of articles per feed
NB_ARTICLES_PER_FEED = getattr(settings, 'NB_ARTICLES_PER_FEED', 10)

# Upload directory name for article's category logos.
ARTICLE_CATEGORY_LOGO_UPLOAD_DIR_NAME = getattr(settings, 'ARTICLE_CATEGORY_LOGO_UPLOAD_DIR_NAME', 'category_logos/')

# Height in pixels of the article's category logo
ARTICLE_CATEGORY_LOGO_HEIGHT = getattr(settings, 'ARTICLE_CATEGORY_LOGO_HEIGHT', 120)

# Width in pixels of the article's category logo
ARTICLE_CATEGORY_LOGO_WIDTH = getattr(settings, 'ARTICLE_CATEGORY_LOGO_WIDTH', 120)

# Number of days before a published article is "old"
NB_DAYS_BEFORE_ARTICLE_GET_OLD = getattr(settings, 'NB_DAYS_BEFORE_ARTICLE_GET_OLD', 31 * 6)
