"""
Data models for the registration app.
"""

import datetime

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.crypto import constant_time_compare
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.template import loader

from .managers import (UserRegistrationManager,
                       BannedUsernameManager,
                       BannedEmailManager)
from .signals import user_activated
from .settings import ACCOUNT_ACTIVATION_TIMEOUT_DAYS


class UserRegistrationProfile(models.Model):
    """
    User registration profile model.
    The ``UserRegistrationProfile`` model store all required information for
    the user registration mechanism to work. Each user (``AUTH_USER_MODEL``)
    of the website can have one - and only one - linked ``UserRegistrationProfile``.
    The ``UserRegistrationProfile`` contain the activation key used to activate the user
    account by email, and the last date of emission of the said email. The
    ``last_key_mailing_date`` field can (but is not currently) used to implemented a
    "please resend the activation mail" page, with anti-dos protection by time slot (no
     mail resend before n hours for example). The ``last_key_mailing_date`` field is
     also used to invalidate the activation key after ``ACCOUNT_ACTIVATION_TIMEOUT_DAYS``
     days. To avoid unused activation key to fill the database it's a good practice to run
     on a regular basis the maintenance/cleanup script (see ``cleanupregistration.py``).
    """

    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                primary_key=True,
                                editable=False,
                                related_name='+',
                                verbose_name=_('Related user'))

    activation_key = models.CharField(_('Activation key'),
                                      db_index=True,  # Database optimization
                                      max_length=32)

    activation_key_used = models.BooleanField(_('Activation key used'),
                                              default=False)

    last_key_mailing_date = models.DateTimeField(_('Last key mailing date'),
                                                 default=None,
                                                 blank=True,
                                                 null=True)

    creation_date = models.DateTimeField(_('Registration date'),
                                         auto_now_add=True)

    objects = UserRegistrationManager()

    class Meta:
        verbose_name = _('User registration profile')
        verbose_name_plural = _('User registration profiles')
        get_latest_by = 'creation_date'
        ordering = ('creation_date', )

    def __str__(self):
        return 'Registration profile for "%s"' % self.user.username

    def activation_key_expired(self, now=None):
        """
        Determine whether this ``UserRegistrationProfile``'s activation
        key has expired, returning a boolean -- ``True`` if the key
        has expired, ``False`` if not expired yet.
        Key expiration is determined by a two-step process:
        1. If the user has already activated. Re-activating is not
           permitted, and so this method returns ``True`` in this case.
        2. Otherwise, the date the user signed up is incremented by
           the number of days specified in the setting
           ``ACCOUNT_ACTIVATION_TIMEOUT_DAYS`` (which should be the number of
           days after signup during which a user is allowed to
           activate their account). If the result is less than or
           equal to the current date, the key has expired and this
           method returns ``True``.
        :param now: Use for testing, if set timezone.now() will not be used.
        """
        if now is None:  # Allow unittest of the function without being time dependent
            now = timezone.now()
        if not self.last_key_mailing_date:
            return self.activation_key_used
        expiration_date = self.last_key_mailing_date + datetime.timedelta(days=ACCOUNT_ACTIVATION_TIMEOUT_DAYS)
        return self.activation_key_used or (now > expiration_date)
    activation_key_expired.boolean = True
    activation_key_expired.short_description = _('Key expired')

    def activation_key_valid(self, activation_key):
        """
        Determine whether the given activation key is valid or not for the current
        ``UserRegistrationProfile``. Return a boolean -- ``True`` if the key is valid.
        Key validity is determined by a three step process:
        1. If the has been already used, the key is invalid.
        2. If the key has expired, the key is invalid.
        3. If the key does not match the one in database (constant time compare), the
        key is invalid.
        If after all the steps above the key still valid, well, the key is valid.
        :param activation_key: The activation key to be tested.
        """
        return not self.activation_key_expired() and constant_time_compare(activation_key, self.activation_key)

    def activate_user(self):
        """
        Activate the account of the associated ``User`` instance. Mark the activation key
        as "used" to avoid later re-activation and turn on the "is_active" flag of the associated
        ``User`` instance. If the user is already activated (multiple call of this function),
        the user is not modified and the ``user_activated`` signal is not sent.
        """
        if not self.activation_key_used:
            self.activation_key_used = True
            self.save(update_fields=('activation_key_used', ))
        if not self.user.is_active:
            self.user.is_active = True
            self.user.save(update_fields=('is_active', ))
            user_activated.send(sender=self.__class__, user=self.user)

    def send_activation_email(self,
                              request,
                              subject_template_name,
                              email_template_name,
                              html_email_template_name=None,
                              use_https=False,
                              from_email=None):
        """
        Send (or resend) the email with the activation link for the current
        ``UserRegistrationProfile`` in it. This function make use of all given
        parameters to render the text-only, and if provided, the html version
        of the email subject and content. The following variables are passed to
        the template rendering engine (for both the text-only and html version):
        - ``email`` what contain the user email address,
        - ``domain`` what contain the current site domain (determined by SITE_ID
        if the sites apps is installed, or using the HTTP Hosts header),
        - ``site_name`` what contain the equivalent of {{ site.name }},
        - ``uid`` with the user ID encoded in base64,
        - ``user`` what contain the ``User`` instance associated with the profile,
        - ``activation_key``what contain the activation key as string,
        - ``protocol``, "http" or "https" according to the ``use_https`` parameter.
        Once the email sent, the function save the current date and time in
        ``last_key_mailing_date`` for dos protection or administrative purpose.
        :param request: The current request object.
        :param subject_template_name: The template name to be used for the mail's subject.
        :param email_template_name: The template name to be used for the email text body.
        :param html_email_template_name: The template name to be used for the email HTML body.
        :param use_https: Set to ``True`` if you want HTTPS for the activation link.
        :param from_email: Set to something not ``None`` if you want to overwrite the default "from" address.
        """
        # Prepare context for the text rendering
        current_site = get_current_site(request)
        site_name = current_site.name
        domain = current_site.domain
        context = {
            'email': self.user.email,
            'domain': domain,
            'site_name': site_name,
            'uid': urlsafe_base64_encode(force_bytes(self.user.pk)),
            'user': self.user,
            'activation_key': self.activation_key,
            'protocol': 'https' if use_https else 'http',
            'activation_timeout_days': ACCOUNT_ACTIVATION_TIMEOUT_DAYS
            }

        # Render the mail's subject and body
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        # craft the email and send it
        email_message = EmailMultiAlternatives(subject, body, from_email, [self.user.email])
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, 'text/html')
        email_message.send(fail_silently=True)

        # Save the current time to avoid sending email too soon if resent needed
        self.last_key_mailing_date = timezone.now()
        self.save(update_fields=('last_key_mailing_date', ))

    def activation_mail_was_sent_recently(self):
        """
        This function return ``True`` if the last activation mail was sent in the
        last hour. Pretty useful for dos-protection or administrative purpose.
        If the mail has never been sent, this function obviously return ``False``.
        """
        if not self.last_key_mailing_date:
            return False
        timeout = self.last_key_mailing_date + datetime.timedelta(hours=1)
        return timezone.now() <= timeout
    activation_mail_was_sent_recently.boolean = True
    activation_mail_was_sent_recently.short_description = _('Mail sent recently')


class BannedUsername(models.Model):
    """
    Simple data model used to store banned username (as simple case-insensitive text).
    Only effective for user registration made through the registration form (not from the admin site).
    """

    username = models.CharField(_('Banned username'),
                                db_index=True,  # Database optimization
                                unique=True,
                                max_length=140)

    objects = BannedUsernameManager()

    class Meta:
        verbose_name = _('Banned username')
        verbose_name_plural = _('Banned usernames')

    def __str__(self):
        return self.username


class BannedEmail(models.Model):
    """
    Simple data model used to store banned email (or email provider) (as case-insensitive text).
    Email address can be in the formats: "user@provider.tld", "user@*", "*@provider.tld" or "*@provider.*".
    Only effective for user registration made through the registration form (not from the admin site).
    """

    email = models.CharField(_('Banned email'),
                             db_index=True,  # Database optimization
                             unique=True,
                             max_length=280)

    objects = BannedEmailManager()

    class Meta:
        verbose_name = _('Banned email')
        verbose_name_plural = _('Banned emails')

    def __str__(self):
        return self.email
