"""
Custom settings for the licenses app.
"""

from django.conf import settings


# Number of content licenses per page (default 25)
NB_LICENSES_PER_PAGE = getattr(settings, 'NB_LICENSES_PER_PAGE', 25)

# Upload directory for license logos
LICENSE_LOGO_UPLOAD_DIR_NAME = getattr(settings, 'LICENSE_LOGO_UPLOAD_DIR_NAME', 'licenses_logo')
