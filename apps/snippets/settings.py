"""
Custom settings for the code snippets app.
"""

from django.conf import settings

# Default number of spaces for each tabulation (0 to disable tabulation expansion)
SNIPPETS_DEFAULT_TABULATION_SIZE = getattr(settings, 'SNIPPETS_DEFAULT_TABULATION_SIZE', 4)

# Display line numbers by default? (True by default)
SNIPPETS_DISPLAY_LINE_NUMBERS_BY_DEFAULT = getattr(settings, 'SNIPPETS_DISPLAY_LINE_NUMBERS_BY_DEFAULT', True)

# Number of code snippets per page
NB_SNIPPETS_PER_PAGE = getattr(settings, 'NB_SNIPPETS_PER_PAGE', 25)

# Number of code snippets per feed
NB_SNIPPETS_PER_FEED = getattr(settings, 'NB_SNIPPETS_PER_FEED', 10)

# Pygments style name to use
SNIPPETS_PYGMENTS_CSS_STYLE_NAME = getattr(settings, 'SNIPPETS_PYGMENTS_CSS_STYLE_NAME', 'default')

# Pygments style namespace to use (default is 'highlight')
SNIPPETS_PYGMENTS_CSS_NAMESPACE = getattr(settings, 'SNIPPETS_PYGMENTS_CSS_NAMESPACE', 'highlight')
