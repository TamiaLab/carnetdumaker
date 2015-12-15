"""
Forms for the notifications app.
"""

from django import forms

from .models import NotificationsUserProfile


class NotificationsProfileModificationForm(forms.ModelForm):
    """
    Notifications user's account modification form.
    """

    class Meta:

        model = NotificationsUserProfile

        fields = ('send_mail_on_new_notification', )
