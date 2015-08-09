"""
Timezones app.

This reusable Django application provide a models/forms field for stored PyTz timezone objects.
This application also provide automatic setup of timezone from the user's preferences in session.
"""

default_app_config = 'apps.timezones.apps.TimezonesConfig'

# Friendly include
from .middleware import TIMEZONE_SESSION_KEY
