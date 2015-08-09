"""
Signals declaration for the user accounts app.
"""

from django.dispatch import Signal


# Emitted when the user update his profile information.
user_profile_updated = Signal(providing_args=['user_profile'])
