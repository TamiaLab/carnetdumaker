"""
Default settings for the user accounts app.
"""

from django.conf import settings


# Height size of the user's avatar picture in pixels (default 120px)
# Also used as minimum height size during upload to avoid up-scaling.
AVATAR_HEIGHT_SIZE_PX = getattr(settings, 'AVATAR_HEIGHT_SIZE_PX', 120)

# Width size of the user's avatar picture in pixels (default 120px)
# Also used as minimum width size during upload to avoid up-scaling.
AVATAR_WIDTH_SIZE_PX = getattr(settings, 'AVATAR_WIDTH_SIZE_PX', 120)

# Maximum upload height size of the user's avatar picture in pixels (default 4000px)
AVATAR_HEIGHT_SIZE_PX_MAX = getattr(settings, 'AVATAR_HEIGHT_SIZE_PX_MAX', 4000)

# Maximum upload width size of the user's avatar picture in pixels (default 4000px)
AVATAR_WIDTH_SIZE_PX_MAX = getattr(settings, 'AVATAR_WIDTH_SIZE_PX_MAX', 4000)

# Avatar upload directory name (default 'avatars')
AVATAR_UPLOAD_DIR_NAME = getattr(settings, 'AVATAR_UPLOAD_DIR_NAME', 'avatars')

# Default timezone of the user (default 'Europe/Paris')
DEFAULT_USER_TIMEZONE = getattr(settings, 'DEFAULT_USER_TIMEZONE', 'Europe/Paris')

# Default country of the user (default 'FRA' for france (see ``countries.py``))
DEFAULT_USER_COUNTRY = getattr(settings, 'DEFAULT_USER_COUNTRY', 'FRA')

# Number of accounts per page on the accounts list view (default 25)
NB_ACCOUNTS_PER_PAGE = getattr(settings, 'NB_ACCOUNTS_PER_PAGE', 25)

# "No avatar" static image url (default 'images/no_avatar.png')
NO_AVATAR_STATIC_URL = getattr(settings, 'NO_AVATAR_STATIC_URL', 'images/no_avatar.png')

# Number of seconds after the last activity timestamp during which the user is considered online (default 15 minutes)
ONLINE_USER_TIME_WINDOW_SECONDS = getattr(settings, 'ONLINE_USER_TIME_WINDOW_SECONDS', 15 * 60)
