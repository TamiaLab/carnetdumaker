"""
User accounts app.

This reusable Django application allow users to have custom accounts on the site.
User accounts store a lot of app-independent information, like socials links, biography, privacy preferences, ...

This app also keep trace of currently online users using the bundled middleware class.
"""

default_app_config = 'apps.accounts.apps.AccountsConfig'
