"""
Data models for the user accounts app.
"""

import os
import datetime

from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from django.core.urlresolvers import reverse_lazy as reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from django.utils import (timezone,
                          translation)
from django.utils.http import urlquote_plus
from django.utils.translation import ugettext_lazy as _

from apps.tools.fields import (AutoOneToOneField,
                               AutoResizingImageField)
from apps.tools.http_utils import get_client_ip_address
from apps.timezones.fields import TimeZoneField
from apps.countries.fields import CountryField
from apps.gender.fields import GenderField
from apps.timezones import TIMEZONE_SESSION_KEY
from apps.txtrender.fields import RenderTextField
from apps.txtrender.utils import render_html
from apps.txtrender.signals import render_engine_changed

from .settings import (AVATAR_HEIGHT_SIZE_PX,
                       AVATAR_WIDTH_SIZE_PX,
                       AVATAR_UPLOAD_DIR_NAME,
                       DEFAULT_USER_TIMEZONE,
                       DEFAULT_USER_COUNTRY,
                       ONLINE_USER_TIME_WINDOW_SECONDS)
from .signals import user_profile_updated
from .managers import UserProfileManager


def _avatar_upload_to(instance, filename):
    """
    ``upload_to`` path generator for the avatar field of user's profiles.
    :param instance: The ``UserProfile`` instance of the user.
    :param filename: The current filename (not used) of the avatar image file.
    :return: The user's avatar image filename with path like "AVATAR_UPLOAD_DIR_NAME/avatar-%(user_id)d.jpg".
    """
    return os.path.join(AVATAR_UPLOAD_DIR_NAME, 'avatar-%d.jpg' % instance.user_id)


class UserProfile(models.Model):
    """
    User profile data model.
    Any extra information about an user not linked to a specific app is stored here.
    This model is linked with the ``AUTH_USER_MODEL`` model by an auto one-to-one relation.
    The user profile is accessible using the backward relation name ``user_profile``.
    Currently the ``UserProfile`` model store:
    - User's avatar (fixed size image) - optional,
    - User's timezone and preferred language,
    - User's country and last login IP address (for legal purposes),
    - User's privacy preferences (first/last names public, email public, search by email allowed, online status public),
    - User's newsletter preference (accept or deny),
    - User's personal information (gender, location, company, biography and signature - HTML is
    allowed in biography and signature),
    - User's social links (website, skype, twitter, facebook, google+, youtube),
    - a modification date (for SEO and feeds),
    - a last activity date for online users tracking.
    """

    user = AutoOneToOneField(settings.AUTH_USER_MODEL,
                             related_name='user_profile',
                             primary_key=True,
                             editable=False,
                             verbose_name=_('Related user'))

    avatar = AutoResizingImageField(_('Avatar'),
                                    upload_to=_avatar_upload_to,
                                    width=AVATAR_WIDTH_SIZE_PX,
                                    height=AVATAR_HEIGHT_SIZE_PX,
                                    default=None,
                                    blank=True,
                                    null=True)

    timezone = TimeZoneField(_('Timezone'),
                             default=DEFAULT_USER_TIMEZONE)

    preferred_language = models.CharField(_('Preferred language'),
                                          max_length=10,
                                          default=settings.LANGUAGE_CODE,
                                          choices=settings.LANGUAGES)

    country = CountryField(_('Country'),
                           default=DEFAULT_USER_COUNTRY)

    last_login_ip_address = models.GenericIPAddressField(_('Last login IP address'),
                                                         default=None,
                                                         editable=False,
                                                         blank=True,
                                                         null=True)

    first_last_names_public = models.BooleanField(_('Last and first names public'),
                                                  default=True)

    email_public = models.BooleanField(_('Email address public'),
                                       default=False)

    search_by_email_allowed = models.BooleanField(_('Search by email address allowed'),
                                                  default=False)

    online_status_public = models.BooleanField(_('Online status public'),
                                               default=True)

    accept_newsletter = models.BooleanField(_('Accept to receive newsletter'),
                                            default=False)

    gender = GenderField(_('Gender'))

    location = models.CharField(_('Location'),
                                max_length=255,
                                default='',
                                blank=True)

    company = models.CharField(_('Company'),
                               max_length=255,
                               default='',
                               blank=True)

    biography = RenderTextField(_('Biography'))

    biography_html = models.TextField(_('Biography (raw HTML)'),
                                      default='',
                                      blank=True)

    signature = RenderTextField(_('Signature'))

    signature_html = models.TextField(_('Signature (raw HTML)'),
                                      default='',
                                      blank=True)

    website_name = models.CharField(_('Website name'),
                                    help_text=_('The website URL will be used if empty.'),
                                    max_length=255,
                                    default='',
                                    blank=True)

    website_url = models.URLField(_('Website url'),
                                  default='',
                                  blank=True)

    jabber_name = models.CharField(_('Jabber nickname'),
                                   max_length=255,
                                   default='',
                                   blank=True)

    skype_name = models.CharField(_('Skype nickname'),
                                  max_length=255,
                                  default='',
                                  blank=True)

    twitter_name = models.CharField(_('Twitter nickname'),
                                    max_length=255,
                                    default='',
                                    blank=True)

    facebook_url = models.CharField(_('Facebook URL'),
                                    max_length=255,
                                    default='',
                                    blank=True,
                                    validators=[
                                        RegexValidator(regex=r"^(?:https?:\/\/)?(?:www\.)?facebook\.com\/"
                                                             r"(?:[\w-]*#!\/)?(?:pages\/)?(?:[\w-]+\/)*([\w.-]+)",
                                                       message=_('Please enter a valid Facebook page or profile URL. '
                                                                 'Examples: https://www.facebook.com/MyPage, '
                                                                 'https://www.facebook.com/pages/MyPage/123456.'),
                                                       code='invalid_facebook_url')
                                    ])

    googleplus_url = models.CharField(_('Google+ URL'),
                                      max_length=255,
                                      default='',
                                      blank=True,
                                      validators=[
                                          RegexValidator(regex=r"^(?:https?:\/\/)?plus\.google\.com\/"
                                                               r"(?:u\/0\/|communities\/)?\+?([\w-]+)(?:\/[\w-]+)?",
                                                         message=_('Please enter a valid Google+ page or profile URL. '
                                                                   'Examples: https://plus.google.com/+MyPage, '
                                                                   'https://plus.google.com/1234536789, '
                                                                   'https://plus.google.com/u/0/+MyPage, '
                                                                   'https://plus.google.com/u/0/123456789.'),
                                                         code='invalid_googleplus_url')
                                      ])

    youtube_url = models.CharField(_('Youtube URL'),
                                   max_length=255,
                                   default='',
                                   blank=True,
                                   validators=[
                                       RegexValidator(regex=r"^(?:https?:\/\/)?(?:www\.)?youtube\.com\/"
                                                            r"(?:c\/|channel\/|user\/)([\w-]+)",
                                                      message=_('Please enter a valid Youtube channel or profile URL. '
                                                                'Examples: https://www.youtube.com/c/MySuperChannel, '
                                                                'https://www.youtube.com/user/MySuperChannel, '
                                                                'https://www.youtube.com/channel/0123456789.'),
                                                      code='invalid_youtube_url')
                                   ])

    last_modification_date = models.DateTimeField(_('Last modification date'),
                                                  auto_now=True)

    last_activity_date = models.DateTimeField(_('Last activity date'),
                                              default=None,
                                              editable=False,
                                              blank=True,
                                              null=True)

    objects = UserProfileManager()

    class Meta:
        verbose_name = _('User profile')
        verbose_name_plural = _('User profiles')
        permissions = (
            # TODO?
            # Permission allow class attr in signature/biography
            # Permission allow list tags in signature/biography
            # Permission allow link tag in signature/biography
            # Permission allow image tag in signature/biography
            # Permission allow block tags (code, pre, quote) in signature/biography
            ('allow_raw_link_in_biography', 'Allow raw link (without forcing nofollow) in biography'),
            ('allow_raw_link_in_signature', 'Allow raw link (without forcing nofollow) in signature'),
        )
        ordering = ('user__username',)

    def __str__(self):
        return 'Profile of "%s"' % self.user.username

    def save(self, *args, **kwargs):
        """
        Save the user's profile. Clear website name if website url is empty.
        Also render the biography and signature HTML versions of the source text.
        :param args: Positional arguments for super()
        :param kwargs: Keyword arguments for super()
        """

        # Render HTML
        self.render_text()

        # Handle erroneous website data
        if self.website_name and not self.website_url:
            self.website_name = ''  # Silent fail

        # Handle website url without name
        if self.website_url and not self.website_name:
            self.website_name = self.website_url

        # Avoid XSS in website url
        if self.website_url and not self.website_url.startswith('http'):
            self.website_url = '%s%s' % ('http://', self.website_url)

        # Remove AT sign before the Twitter username if exist
        if self.twitter_name.startswith('@'):
            self.twitter_name = self.twitter_name[1:]

        # Avoid social URLs without scheme
        if self.facebook_url and not self.facebook_url.startswith('http'):
            self.facebook_url = '%s%s' % ('https://', self.facebook_url)
        if self.googleplus_url and not self.googleplus_url.startswith('http'):
            self.googleplus_url = '%s%s' % ('https://', self.googleplus_url)
        if self.youtube_url and not self.youtube_url.startswith('http'):
            self.youtube_url = '%s%s' % ('https://', self.youtube_url)

        # Save the model
        super(UserProfile, self).save(*args, **kwargs)

        # Emit the profile updated signal
        user_profile_updated.send(sender=self.__class__, user_profile=self)

    def save_no_rendering(self, *args, **kwargs):
        """
        Save the model without doing any text rendering or so.
        :param args: For super.save()
        :param kwargs: For super.save()
        :return: None
        """

        # Save the model
        super(UserProfile, self).save(*args, **kwargs)

    def get_absolute_url(self):
        """
        Return the permalink for this user's profile.
        """
        return reverse('accounts:user_profile', kwargs={'username': self.user.username})

    def render_text(self, save=False):
        """
        Render the biography and signature. Save the model only if ``save`` is True.
        :param save: Set to True to save the model after rendering (default is False).
        """

        # Render HTML
        force_nofollow_in_biography = not self.user.has_perm('accounts.allow_raw_link_in_biography')
        self.biography_html = render_html(self.biography, force_nofollow=force_nofollow_in_biography)
        force_nofollow_in_signature = not self.user.has_perm('accounts.allow_raw_link_in_signature')
        self.signature_html = render_html(self.signature, force_nofollow=force_nofollow_in_signature)
        # TODO filter more tag in signature (like h1, h2, h3, etc, ...)

        # Save if required
        if save:
            # Avoid infinite loop by calling directly super.save
            super(UserProfile, self).save(update_fields=('biography_html', 'signature_html'))

    def is_online(self):
        """
        Return ``True`` if the user is online and don't hide this information.
        """
        if self.last_activity_date is None:
            return False
        offline_threshold = timezone.now() - datetime.timedelta(seconds=ONLINE_USER_TIME_WINDOW_SECONDS)
        return self.online_status_public and self.last_activity_date > offline_threshold
    is_online.short_description = _('Is online')
    is_online.boolean = True

    def get_jabber_url(self):
        """
        Return the link to the user's jabber account.
        """
        return 'xmpp:%s' % urlquote_plus(self.jabber_name)

    def get_skype_url(self):
        """
        Return the link to the user's skype account.
        """
        return 'skype:%s?call' % urlquote_plus(self.skype_name)

    def get_twitter_url(self):
        """
        Return the link to the user's twitter account.
        """
        return 'https://twitter.com/%s' % urlquote_plus(self.twitter_name)


def _redo_profile_text_rendering(sender, **kwargs):
    """
    Redo text rendering of all user profile.
    :param sender: Not used.
    :param kwargs: Not used.
    """
    for profile in UserProfile.objects.all():
        profile.render_text(save=True)

render_engine_changed.connect(_redo_profile_text_rendering)


def _set_preferred_language_and_timezone(sender, user, request, **kwargs):
    """
    Set preferred language and timezone upon login.
    :param sender: Not used.
    :param user: Just logged in User instance.
    :param request: The current request object.
    :param kwargs: Not used.
    """
    user_profile = user.user_profile

    # Activate timezone for the current thread, and store value for any future requests
    user_timezone = user_profile.timezone
    timezone.activate(user_timezone)
    request.session[TIMEZONE_SESSION_KEY] = user_timezone.zone

    # Activate language for the current thread, and store value for any future requests
    user_language = user_profile.preferred_language
    translation.activate(user_language)
    request.session[translation.LANGUAGE_SESSION_KEY] = user_language
    request.LANGUAGE_CODE = translation.get_language()

user_logged_in.connect(_set_preferred_language_and_timezone)


def _store_current_ip_address(sender, user, request, **kwargs):
    """
    Store the current IP address of the user.
    :param sender: Not used.
    :param user: Just logged in User instance.
    :param request: The current request object.
    :param kwargs: Not used.
    """
    ip_address = get_client_ip_address(request)
    user_profile = user.user_profile
    user_profile.last_login_ip_address = ip_address
    user_profile.save_no_rendering(update_fields=('last_login_ip_address',))

user_logged_in.connect(_store_current_ip_address)


def get_online_users_queryset():
    """
    Return a queryset of all currently online users.
    """
    offline_threshold = timezone.now() - datetime.timedelta(seconds=ONLINE_USER_TIME_WINDOW_SECONDS)
    return get_user_model().objects.filter(user_profile__online_status_public=True,
                                           user_profile__last_activity_date__isnull=False,
                                           user_profile__last_activity_date__gt=offline_threshold)
