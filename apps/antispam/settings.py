"""
Default settings for the anti-spam app.
"""

from django.conf import settings


# Minimum of time (in seconds) between the form generation and the form submission (default 5 seconds)
MIN_TIME_FORM_GENERATION_SUBMIT = getattr(settings, 'MIN_TIME_FORM_GENERATION_SUBMIT', 5)

# Maximum of time (in seconds) between the form generation and the form submission (default 30 minutes)
MAX_TIME_FORM_GENERATION_SUBMIT = getattr(settings, 'MAX_TIME_FORM_GENERATION_SUBMIT', 60 * 30)

# Set to True to disable completely the antispam verification (default False)
DISABLE_ANTISPAM_VERIFICATION = getattr(settings, 'DISABLE_ANTISPAM_VERIFICATION', False)
