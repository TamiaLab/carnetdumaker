"""
Signals declaration for the registration app.
"""

from django.dispatch import Signal


# A new user has registered.
user_registered = Signal(providing_args=['user'])

# A user has activated his or her account.
user_activated = Signal(providing_args=['user'])
