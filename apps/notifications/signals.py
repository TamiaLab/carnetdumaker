"""
Signals declaration for the notifications apps.
"""

from django.dispatch import Signal


# A new notification has been created.
new_notification = Signal(providing_args=["notification"])

# Notification get read/dismiss
dismiss_notification = Signal(providing_args=["notification"])

# Notification get unread
unread_notification = Signal(providing_args=["notification"])
