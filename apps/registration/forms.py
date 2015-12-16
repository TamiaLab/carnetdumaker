"""
Forms for the registration app.
"""

from django import forms
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse_lazy
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from apps.antispam.forms import AntispamHoneypotFormMixin

from .models import (UserRegistrationProfile,
                     BannedUsername,
                     BannedEmail)
from .settings import MIN_PASSWORD_SIZE


class BaseUserRegistrationForm(forms.Form):
    """
    The ``BaseUserRegistrationForm`` form handle all the classic registration stuff,
    like username, email address (double-typed) and password (also double-typed). Feel
    free to overload this base class to add more stuff in it (like, terms-of-service checkbox
    or anything else).
    """

    username = forms.RegexField(regex=r'^[\w.@+-]+$',
                                max_length=30,
                                label=_('Username'),
                                error_messages={'invalid': _('The username may contain only letters, '
                                                             'numbers and @.+-_ characters.')})
    email1 = forms.EmailField(label=_('E-mail'),
                              max_length=255)

    email2 = forms.EmailField(label=_('E-mail (again)'),
                              max_length=255)

    password1 = forms.CharField(widget=forms.PasswordInput,
                                min_length=MIN_PASSWORD_SIZE,
                                label=_('Password'))

    password2 = forms.CharField(widget=forms.PasswordInput,
                                min_length=MIN_PASSWORD_SIZE,
                                label=_('Password (again)'))

    def clean_username(self):
        """
        Validate that the username is not banned and is not already in use.
        """
        username = self.cleaned_data['username']
        if BannedUsername.objects.is_username_banned(username):
            raise forms.ValidationError(_('This username is not allowed, please chose another one.'),
                                        code='username_disallowed')
        existing_user = get_user_model().objects.filter(username__iexact=username)
        if existing_user.exists():
            raise forms.ValidationError(_('An user with that username already exists.'),
                                        code='username_already_exist')
        return self.cleaned_data['username']

    def clean_email1(self):
        """
        Validate that the email address is not already in use.
        """
        email = self.cleaned_data['email1']
        if '+' in email:
            raise forms.ValidationError(_('Plus sign (+) is not allowed in the email address,'
                                          ' please chose another one.'),
                                        code='email_alias_disallowed')
        if BannedEmail.objects.is_email_address_banned(email):
            raise forms.ValidationError(_('This email address or email provider '
                                          'is not allowed, please chose another one.'),
                                        code='email_disallowed')
        existing_email = get_user_model().objects.filter(email__iexact=email)
        if existing_email.exists():
            raise forms.ValidationError(_('An user with that email address already exists.'),
                                        code='email_already_exist')
        return self.cleaned_data['email1']

    def clean_email2(self):
        """
        Verify that the values entered into the two email fields match.
        """
        if 'email1' in self.cleaned_data \
                and 'email2' in self.cleaned_data \
                and self.cleaned_data['email1'] != self.cleaned_data['email2']:
            raise forms.ValidationError(_("The two email fields didn't match."),
                                        code='email_mismatch')
        return self.cleaned_data['email2']

    def clean_password2(self):
        """
        Verify that the values entered into the two password fields
        match.
        """
        if 'password1' in self.cleaned_data \
                and 'password2' in self.cleaned_data \
                and self.cleaned_data['password1'] != self.cleaned_data['password2']:
            raise forms.ValidationError(_("The two password fields didn't match."),
                                        code='password_mismatch')
        return self.cleaned_data['password2']

    def save(self,
             request,
             subject_template_name,
             email_template_name,
             html_email_template_name=None,
             use_https=False,
             from_email=None):
        """
        Save the form data by creating a new inactive user and registration profile,
        then send the activation link by email.
        :param request: the current request.
        :param subject_template_name: The template name to be used for the mail's subject.
        :param email_template_name: The template name to be used for the mail's text body.
        :param html_email_template_name: The template name to be used for the mail's HTML body.
        :param use_https: Set to ``True`` for HTTPS, ``False`` for HTTP.
        :param from_email: "from" email, if ``None`` default settings address is used.
        """
        username = self.cleaned_data['username']
        email = self.cleaned_data['email1']
        password = self.cleaned_data['password1']
        profile = UserRegistrationProfile.objects.create_inactive_user(username, email, password)
        profile.send_activation_email(subject_template_name=subject_template_name,
                                      email_template_name=email_template_name,
                                      html_email_template_name=html_email_template_name,
                                      use_https=use_https,
                                      from_email=from_email,
                                      request=request)


class UserRegistrationForm(AntispamHoneypotFormMixin, BaseUserRegistrationForm):
    """
    Form for registering a new user account. Same as ``BaseUserRegistrationForm``
    but also require that the user agree with the terms of service, and kick out
    bots by using an honeypot field (simple solution, but powerful).
    """

    tos_link = reverse_lazy('staticpages:tos')

    tos = forms.BooleanField(widget=forms.CheckboxInput,
                             error_messages={'required': _("You must agree to the terms to register.")})

    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['tos'].label = mark_safe(_('I have read and agree to the '
                                               '<a href="%s">Terms of Service</a>') % self.tos_link)
