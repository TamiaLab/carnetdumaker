"""
Forms for the private messages app.
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model

from apps.txtrender.forms import MarkupCharField
from apps.txtrender.utils import render_quote

from .models import (PrivateMessage,
                     PrivateMessageUserProfile,
                     BlockedUser)


def _re_subject(subject):
    """
    Add "Re:" to the subject if not already in.
    :param subject: The current subject.
    :return: The subject with "Re:" prefix.
    """
    if not subject:
        return 'Re:'
    elif not subject.startswith('Re:'):
        return 'Re: %s' % subject[:250]
    else:
        return subject


class PrivateMessageCreationForm(forms.Form):
    """
    ``PrivateMessage`` creation form without parent message.
    """

    subject = forms.CharField(max_length=255,
                              required=False,
                              label=_('Subject'))

    recipient = forms.CharField(max_length=30,
                                label=_('Recipient'))

    body = MarkupCharField(label=_('Body'))

    def __init__(self, *args, **kwargs):
        self.sender = kwargs.pop('sender', None)
        assert self.sender is not None
        super(PrivateMessageCreationForm, self).__init__(*args, **kwargs)

    def clean_recipient(self):
        """
        Validate that the recipient username is valid.
        """
        recipient_name = self.cleaned_data['recipient']
        if ',' in recipient_name or ';' in recipient_name:
            raise ValidationError(_('You can send a private message to only one recipient.'),
                                  code='multiple_recipients')
        try:
            recipient_obj = get_user_model().objects.select_related('privatemsg_profile') \
                .get(username__iexact=recipient_name)
        except get_user_model().DoesNotExist:
            raise ValidationError(_('Unknown recipient "%(username)s".'),
                                  code='unknown_recipient', params={'username': recipient_name})
        if not recipient_obj.is_active:
            raise ValidationError(_('The recipient has closed his acccount.'),
                                  code='recipient_account_closed')
        if not recipient_obj.privatemsg_profile.accept_privmsg:
            raise ValidationError(_('The recipient does not accept private messages.'),
                                  code='recipient_refuse_privatemsg')
        if BlockedUser.objects.has_blocked_user(recipient_obj, self.sender):
            raise ValidationError(_('The recipient does not accept private messages from you.'),
                                  code='recipient_has_blocked_user')
        return recipient_obj

    def save(self):
        """
        Save the form by creating a new PrivateMessage object
        """
        new_obj = PrivateMessage.objects.create(subject=self.cleaned_data['subject'],
                                                body=self.cleaned_data['body'],
                                                recipient=self.cleaned_data['recipient'],
                                                sender=self.sender)

        # Return the newly created object
        return new_obj


class PrivateMessageReplyForm(forms.Form):
    """
    ``PrivateMessage`` creation form with parent message (reply).
    Recipient fixed to the parent message's recipient to avoid messing up message's threads.
    """

    subject = forms.CharField(max_length=255,
                              required=False,
                              label=_('Subject'))

    body = MarkupCharField(label=_('Body'))

    def __init__(self, *args, **kwargs):
        self.parent_msg = kwargs.pop('parent_msg', None)
        assert self.parent_msg is not None
        self.sender = kwargs.pop('sender', None)
        assert self.sender is not None
        super(PrivateMessageReplyForm, self).__init__(*args, **kwargs)

        # Pre-fill subject and body
        self.fields['subject'].initial = _re_subject(self.parent_msg.subject)
        self.fields['body'].initial = render_quote(self.parent_msg.body,
                                                   self.parent_msg.sender.username,
                                                   self.parent_msg.get_absolute_url())

    def clean(self):
        """
        Validate that the recipient accept the reply.
        """
        recipient_obj = self.parent_msg.sender
        if not recipient_obj.privatemsg_profile.accept_privmsg:
            raise ValidationError(_('The recipient does not accept private messages.'),
                                  code='recipient_refuse_privatemsg')
        if BlockedUser.objects.has_blocked_user(recipient_obj, self.sender):
            raise ValidationError(_('The recipient does not accept private messages from you.'),
                                  code='recipient_has_blocked_user')
        return self.cleaned_data

    def save(self):
        """
        Save the form by creating a new PrivateMessage object
        """
        new_obj = PrivateMessage.objects.create(subject=self.cleaned_data['subject'],
                                                body=self.cleaned_data['body'],
                                                recipient=self.parent_msg.sender,
                                                sender=self.sender,
                                                parent_msg=self.parent_msg)

        # Return the newly created object
        return new_obj


class PrivateMessageProfileModificationForm(forms.ModelForm):
    """
    Private message user's account modification form.
    """

    class Meta:

        model = PrivateMessageUserProfile

        fields = ('notify_on_new_privmsg',
                  'accept_privmsg')
