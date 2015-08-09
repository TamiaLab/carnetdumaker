"""
Change email app.

This reusable Django application allow users to change their email address.
The current email address is not altered until the confirmation link (sent mail at the new address) is clicked.
"""

default_app_config = 'apps.changemail.apps.ChangeEmailConfig'
