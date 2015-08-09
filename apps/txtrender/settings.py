"""
Custom settings for the text rendering app.
"""

from django.conf import settings

# Default number of spaces for each tabulation (0 to disable tabulation expansion)
DEFAULT_TABULATION_SIZE = getattr(settings, 'DEFAULT_TABULATION_SIZE', 4)

# Display line numbers by default? (True by default)
DISPLAY_LINE_NUMBERS_BY_DEFAULT = getattr(settings, 'DISPLAY_LINE_NUMBERS_BY_DEFAULT', True)

# Pygments style name to use
PYGMENTS_CSS_STYLE_NAME = getattr(settings, 'PYGMENTS_CSS_STYLE_NAME', 'default')

# Pygments style namespace to use (default is 'highlight')
PYGMENTS_CSS_NAMESPACE = getattr(settings, 'PYGMENTS_CSS_NAMESPACE', 'highlight')
