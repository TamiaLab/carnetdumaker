"""
User API keys app.

This reusable Django application allow users to have API keys for various purposes (API access,
authenticated feeds access, etc.). This application include a view for regenerating the user API key if compromised.
"""

default_app_config = 'apps.userapikey.apps.UserApiKeyConfig'
