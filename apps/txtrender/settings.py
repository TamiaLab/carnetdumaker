"""
Custom settings for the text rendering app.
"""

from django.conf import settings


# Emoticons images directory path with trailing slash
EMOTICONS_IMG_DIR = getattr(settings, 'EMOTICONS_IMG_DIR', 'images/smileys/')

# Base URL for relative-to-absolute conversion
RELATIVE_URL_BASE = getattr(settings, 'RELATIVE_URL_BASE', 'https://www.carnetdumaker.net/')
