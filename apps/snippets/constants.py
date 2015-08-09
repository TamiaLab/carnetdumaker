"""
Constants for the code snippets app.
"""

from pygments.lexers import get_all_lexers


# Populate the list of available lexers
CODE_LANGUAGE_CHOICES = []
for name, aliases, filetypes, mimetypes in get_all_lexers():
    CODE_LANGUAGE_CHOICES.append((aliases[0], name))
CODE_LANGUAGE_CHOICES = list(sorted(CODE_LANGUAGE_CHOICES, key=lambda x: x[0]))

# Default "no-op" lexer name
CODE_LANGUAGE_DEFAULT = 'text'
