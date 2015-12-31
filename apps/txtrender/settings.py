"""
Custom settings for the text rendering app.
"""

from django.conf import settings


# Emoticons images directory path with trailing slash
EMOTICONS_IMG_DIR = getattr(settings, 'EMOTICONS_IMG_DIR', 'images/smileys/')
