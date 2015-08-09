"""
Test suite for the models of the user accounts app.
"""

import pytz
import datetime
from unittest import mock

from django.test import TestCase, Client
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone, translation

from apps.timezones import TIMEZONE_SESSION_KEY
from apps.gender.constants import GENDER_UNKNOWN

from ..models import UserProfile, get_online_users_queryset
from ..settings import (DEFAULT_USER_TIMEZONE,
                        DEFAULT_USER_COUNTRY,
                        ONLINE_USER_TIME_WINDOW_SECONDS)
from ..signals import user_profile_updated


class UserProfileTestCase(TestCase):
    """
    Test case for the ``UserProfile`` data model.
    """

    def _get_anon_profile(self):
        """
        Create a new anonymous user named "johndoe" and his related user's profile.
        :return: The newly create user's profile.
        """
        user = get_user_model().objects.create_user(username='johndoe',
                                                    password='illpassword',
                                                    email='john.doe@example.com')
        return user.user_profile

    def test_auto_create(self):
        """
        Test the auto creation of user's profile.
        """
        user = get_user_model().objects.create_user(username='ritokun',
                                                    password='watchfortheplot',
                                                    email='rito.kun@example.com')
        profile = user.user_profile
        self.assertIsNotNone(profile)

    def test_default_values(self):
        """
        Test default values of user's profile.
        THIS TEST ASSERT CRITICAL LEGAL DEFAULTS - DO NOT PUSH TO PROD IF TEST FAILED.
        """
        now = timezone.now()
        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = now
            p = self._get_anon_profile()
            self.assertEqual(None, p.avatar)
            self.assertEqual(DEFAULT_USER_TIMEZONE, p.timezone.zone)
            self.assertEqual(settings.LANGUAGE_CODE, p.preferred_language)
            self.assertEqual(DEFAULT_USER_COUNTRY, p.country)
            self.assertEqual(None, p.last_login_ip_address)
            self.assertTrue(p.first_last_names_public)
            self.assertFalse(p.email_public)
            self.assertFalse(p.search_by_email_allowed)
            self.assertTrue(p.online_status_public)
            self.assertFalse(p.accept_newsletter)
            self.assertEqual(GENDER_UNKNOWN, p.gender)
            self.assertEqual('', p.location)
            self.assertEqual('', p.company)
            self.assertEqual('', p.biography)
            self.assertEqual('', p.biography_html)
            self.assertEqual('', p.signature)
            self.assertEqual('', p.signature_html)
            self.assertEqual('', p.website_name)
            self.assertEqual('', p.website_url)
            self.assertEqual('', p.jabber_name)
            self.assertEqual('', p.skype_name)
            self.assertEqual('', p.twitter_name)
            self.assertEqual('', p.facebook_url)
            self.assertEqual('', p.googleplus_url)
            self.assertEqual('', p.youtube_url)
            self.assertEqual(now, p.last_modification_date)
            self.assertEqual(None, p.last_activity_date)

    def test_str_method(self):
        """
        Test __str__ result for other tests.
        """
        p = self._get_anon_profile()
        self.assertEqual('Profile of "%s"' % p.user.username, str(p))

    def test_get_absolute_url_method(self):
        """
        Test get_absolute_url method with a valid username.
        """
        p = self._get_anon_profile()
        excepted_url = reverse('accounts:user_profile', kwargs={'username': p.user.username})
        self.assertEqual(excepted_url, p.get_absolute_url())

    def test_website_url(self):
        """
        Test website_url and website_name fields with valid values.
        """
        p = self._get_anon_profile()
        p.website_url = 'http://example.com/'
        p.website_name = 'example'
        p.save()
        self.assertEqual('http://example.com/', p.website_url)
        self.assertEqual('example', p.website_name)

    def test_website_url_https(self):
        """
        Test website_url and website_name fields with valid values (HTTPS link).
        """
        p = self._get_anon_profile()
        p.website_url = 'https://example.com/'
        p.website_name = 'example'
        p.save()
        self.assertEqual('https://example.com/', p.website_url)
        self.assertEqual('example', p.website_name)

    def test_website_url_xss(self):
        """
        Test website_url and website_name fields with invalid values (XSS attempt).
        """
        p = self._get_anon_profile()
        p.website_url = 'javascript:alert("XSS")'
        p.website_name = 'Powned'
        p.save()
        self.assertEqual('http://javascript:alert("XSS")', p.website_url)
        self.assertEqual('Powned', p.website_name)

    def test_cleanup_website_name_when_no_url(self):
        """
        Test website_name auto cleaning when no website_url set.
        """
        p = self._get_anon_profile()
        p.website_url = ''
        p.website_name = 'something'
        p.save()
        self.assertEqual('', p.website_url)
        self.assertEqual('', p.website_name)

    def test_auto_website_name_when_no_name(self):
        """
        Test website_name auto setup when no website_name set.
        """
        p = self._get_anon_profile()
        p.website_url = 'http://example.com/'
        p.website_name = ''
        p.save()
        self.assertEqual('http://example.com/', p.website_url)
        self.assertEqual('http://example.com/', p.website_name)

    def test_social_link(self):
        """
        Test all social links display functions.
        """
        p = self._get_anon_profile()
        p.jabber_name = 'jabberuser'
        p.skype_name = 'skypeuser'
        p.twitter_name = 'twitteruser'
        p.save()
        self.assertEqual('xmpp:jabberuser', p.get_jabber_url())
        self.assertEqual('skype:skypeuser?call', p.get_skype_url())
        self.assertEqual('https://twitter.com/twitteruser', p.get_twitter_url())

    def test_twitter_at_sign_removing(self):
        """
        Test if the at sign @ is removed from the beginning of the username.
        """
        p = self._get_anon_profile()
        p.twitter_name = '@twitteruser'
        p.save()
        self.assertEqual('twitteruser', p.twitter_name)
        self.assertEqual('https://twitter.com/twitteruser', p.get_twitter_url())

    def test_facebook_valid_urls(self):
        """
        Test facebook link for validation with valid urls.
        """
        test_urls = (
            'facebook.com/PAGENAME',
            'www.facebook.com/PAGENAME',
            'http://facebook.com/PAGENAME',
            'http://www.facebook.com/PAGENAME',
            'https://facebook.com/PAGENAME',
            'https://www.facebook.com/PAGENAME',

            'facebook.com/PAGE.NAME',
            'www.facebook.com/PAGE.NAME',
            'http://facebook.com/PAGE.NAME',
            'http://www.facebook.com/PAGE.NAME',
            'https://facebook.com/PAGE.NAME',
            'https://www.facebook.com/PAGE.NAME',

            'facebook.com/pages/PAGENAME/PAGEID',
            'www.facebook.com/pages/PAGENAME/PAGEID',
            'http://facebook.com/pages/PAGENAME/PAGEID',
            'http://www.facebook.com/pages/PAGENAME/PAGEID',
            'https://facebook.com/pages/PAGENAME/PAGEID',
            'https://www.facebook.com/pages/PAGENAME/PAGEID',

            'facebook.com/pages/PAGENAME/PAGEID?v=app_123456',
            'www.facebook.com/pages/PAGENAME/PAGEID?v=app_123456',
            'http://facebook.com/pages/PAGENAME/PAGEID?v=app_123456',
            'http://www.facebook.com/pages/PAGENAME/PAGEID?v=app_123456',
            'https://facebook.com/pages/PAGENAME/PAGEID?v=app_123456',
            'https://www.facebook.com/pages/PAGENAME/PAGEID?v=app_123456',

            'facebook.com/pages/PAGENAME/VANITYURL/PAGEID?v=app_132456',
            'www.facebook.com/pages/PAGENAME/VANITYURL/PAGEID?v=app_132456',
            'http://facebook.com/pages/PAGENAME/VANITYURL/PAGEID?v=app_132456',
            'http://www.facebook.com/pages/PAGENAME/VANITYURL/PAGEID?v=app_132456',
            'https://facebook.com/pages/PAGENAME/VANITYURL/PAGEID?v=app_132456',
            'https://www.facebook.com/pages/PAGENAME/VANITYURL/PAGEID?v=app_132456',

            'facebook.com/#!/PAGEID',
            'www.facebook.com/#!/PAGEID',
            'http://facebook.com/#!/PAGEID',
            'http://www.facebook.com/#!/PAGEID',
            'https://facebook.com/#!/PAGEID',
            'https://www.facebook.com/#!/PAGEID',

            'facebook.com/PAGENAME#!/pages/VANITYURL/45678',
            'www.facebook.com/PAGENAME#!/pages/VANITYURL/45678',
            'http://facebook.com/PAGENAME#!/pages/VANITYURL/45678',
            'http://www.facebook.com/PAGENAME#!/pages/VANITYURL/45678',
            'https://facebook.com/PAGENAME#!/pages/VANITYURL/45678',
            'https://www.facebook.com/PAGENAME#!/pages/VANITYURL/45678',

            'facebook.com/PAGENAME#!/PAGEID?v=app_123465',
            'www.facebook.com/PAGENAME#!/PAGEID?v=app_123465',
            'http://facebook.com/PAGENAME#!/PAGEID?v=app_123465',
            'http://www.facebook.com/PAGENAME#!/PAGEID?v=app_123465',
            'https://facebook.com/PAGENAME#!/PAGEID?v=app_123465',
            'https://www.facebook.com/PAGENAME#!/PAGEID?v=app_123465',
        )
        p = self._get_anon_profile()
        for test_url in test_urls:
            p.facebook_url = test_url
            p.full_clean()
            self.assertEqual(test_url, p.facebook_url)

    def test_facebook_invalid_urls(self):
        """
        Test facebook link for validation with invalid urls.
        """
        test_urls = (
            'example.com/PAGENAME',
            'www.example.com/PAGENAME',
            'http://example.com/PAGENAME',
            'http://www.example.com/PAGENAME',
            'https://example.com/PAGENAME',
            'https://www.example.com/PAGENAME',
        )
        p = self._get_anon_profile()
        for test_url in test_urls:
            p.facebook_url = test_url
            with self.assertRaises(ValidationError) as ve:
                p.full_clean()
            self.assertEqual(len(ve.exception.error_dict), 1)
            self.assertEqual(len(ve.exception.error_dict['facebook_url']), 1)
            self.assertEqual(ve.exception.error_dict['facebook_url'][0].code, 'invalid_facebook_url')

    def test_facebook_url_without_protocol(self):
        """
        Test facebook URL without protocol.
        """
        p = self._get_anon_profile()
        p.facebook_url = 'facebook.com/PAGENAME'
        p.save()
        self.assertEqual('https://facebook.com/PAGENAME', p.facebook_url)

    def test_googleplus_valid_urls(self):
        """
        Test Google+ link for validation with valid urls.
        """
        test_urls = (
            'plus.google.com/+USERNAME/PAGE',
            'http://plus.google.com/+USERNAME/PAGE',
            'https://plus.google.com/+USERNAME/PAGE',

            'plus.google.com/u/0/+USERNAME/PAGE',
            'http://plus.google.com/u/0/+USERNAME/PAGE',
            'https://plus.google.com/u/0/+USERNAME/PAGE',

            'plus.google.com/USERID/PAGE',
            'http://plus.google.com/USERID/PAGE',
            'https://plus.google.com/USERID/PAGE',

            'plus.google.com/u/0/USERID/PAGE',
            'http://plus.google.com/u/0/USERID/PAGE',
            'https://plus.google.com/u/0/USERID/PAGE',

            'plus.google.com/communities/USERID/PAGE',
            'http://plus.google.com/communities/USERID/PAGE',
            'https://plus.google.com/communities/USERID/PAGE',
        )
        p = self._get_anon_profile()
        for test_url in test_urls:
            p.googleplus_url = test_url
            p.full_clean()
            self.assertEqual(test_url, p.googleplus_url)

    def test_googleplus_invalid_urls(self):
        """
        Test Google+ link for validation with invalid urls.
        """
        test_urls = (
            'example.com/+USERNAME/PAGE',
            'plus.example.com/+USERNAME/PAGE',
            'http://plus.example.com/+USERNAME/PAGE',
            'https://plus.example.com/+USERNAME/PAGE',
        )
        p = self._get_anon_profile()
        for test_url in test_urls:
            p.googleplus_url = test_url
            with self.assertRaises(ValidationError) as ve:
                p.full_clean()
            self.assertEqual(len(ve.exception.error_dict), 1)
            self.assertEqual(len(ve.exception.error_dict['googleplus_url']), 1)
            self.assertEqual(ve.exception.error_dict['googleplus_url'][0].code, 'invalid_googleplus_url')

    def test_googleplus_url_without_protocol(self):
        """
        Test Google+ URL without protocol.
        """
        p = self._get_anon_profile()
        p.googleplus_url = 'plus.google.com/+USERNAME/PAGE'
        p.save()
        self.assertEqual('https://plus.google.com/+USERNAME/PAGE', p.googleplus_url)

    def test_youtube_valid_urls(self):
        """
        Test Youtube link for validation with valid urls.
        """
        test_urls = (
            'www.youtube.com/c/USERNAME',
            'youtube.com/c/USERNAME',
            'http://www.youtube.com/c/USERNAME',
            'http://youtube.com/c/USERNAME',
            'https://www.youtube.com/c/USERNAME',
            'https://youtube.com/c/USERNAME',

            'www.youtube.com/user/USERNAME',
            'youtube.com/user/USERNAME',
            'http://www.youtube.com/user/USERNAME',
            'http://youtube.com/user/USERNAME',
            'https://www.youtube.com/user/USERNAME',
            'https://youtube.com/user/USERNAME',

            'www.youtube.com/channel/CHANNELID',
            'youtube.com/channel/CHANNELID',
            'http://www.youtube.com/channel/CHANNELID',
            'http://youtube.com/channel/CHANNELID',
            'https://www.youtube.com/channel/CHANNELID',
            'https://youtube.com/channel/CHANNELID',
        )
        p = self._get_anon_profile()
        for test_url in test_urls:
            p.youtube_url = test_url
            p.full_clean()
            self.assertEqual(test_url, p.youtube_url)

    def test_youtube_invalid_urls(self):
        """
        Test Youtube link for validation with invalid urls.
        """
        test_urls = (
            'www.example.com/c/USERNAME',
            'example.com/c/USERNAME',
            'http://www.example.com/c/USERNAME',
            'http://example.com/c/USERNAME',
            'https://www.example.com/c/USERNAME',
            'https://example.com/c/USERNAME',
        )
        p = self._get_anon_profile()
        for test_url in test_urls:
            p.youtube_url = test_url
            with self.assertRaises(ValidationError) as ve:
                p.full_clean()
            self.assertEqual(len(ve.exception.error_dict), 1)
            self.assertEqual(len(ve.exception.error_dict['youtube_url']), 1)
            self.assertEqual(ve.exception.error_dict['youtube_url'][0].code, 'invalid_youtube_url')

    def test_youtube_url_without_protocol(self):
        """
        Test Youtube URL without protocol.
        """
        p = self._get_anon_profile()
        p.youtube_url = 'www.youtube.com/c/USERNAME'
        p.save()
        self.assertEqual('https://www.youtube.com/c/USERNAME', p.youtube_url)

    def test_load_prefs_upon_login(self):
        """
        Test loading of user's preferences upon login.
        """
        p = self._get_anon_profile()
        p.timezone = pytz.timezone('Europe/Paris')
        p.preferred_language = 'fr'
        p.save()
        c = Client()
        c.login(username='johndoe', password='illpassword')

        # Current thread setting tests
        self.assertEqual(p.timezone.zone, timezone.get_current_timezone_name())
        self.assertEqual(p.preferred_language, translation.get_language())

        # Persistence tests
        self.assertIn(TIMEZONE_SESSION_KEY, c.session)
        self.assertEqual(p.timezone.zone, c.session[TIMEZONE_SESSION_KEY])
        self.assertIn(translation.LANGUAGE_SESSION_KEY, c.session)
        self.assertEqual(p.preferred_language, c.session[translation.LANGUAGE_SESSION_KEY])

    def test_save_ip_upon_login(self):
        """
        Test of user's IP address upon login.
        """
        get_user_model().objects.create_user(username='banguy',
                                             password='imthedevil',
                                             email='hax0r@example.com')
        c = Client(REMOTE_ADDR='192.168.1.1')
        response = c.post(reverse('auth:login'), {'username': 'banguy', 'password': 'imthedevil'})
        self.assertIsNotNone(response)
        p = UserProfile.objects.get(user__username='banguy')
        self.assertEqual('192.168.1.1', p.last_login_ip_address)

    def test_is_online_with_user_online(self):
        """
        Test the ``is_online`` for an online user.
        """
        now = timezone.now() - datetime.timedelta(seconds=ONLINE_USER_TIME_WINDOW_SECONDS - 1)
        p = self._get_anon_profile()
        p.online_status_public = True
        p.last_activity_date = now
        self.assertTrue(p.is_online())

    def test_is_online_with_user_online_but_hidden(self):
        """
        Test the ``is_online`` for an online user but hidden.
        """
        now = timezone.now() - datetime.timedelta(seconds=ONLINE_USER_TIME_WINDOW_SECONDS - 1)
        p = self._get_anon_profile()
        p.online_status_public = False
        p.last_activity_date = now
        self.assertFalse(p.is_online())

    def test_is_online_with_user_offline(self):
        """
        Test the ``is_online`` for an offline user.
        """
        now = timezone.now() - datetime.timedelta(seconds=ONLINE_USER_TIME_WINDOW_SECONDS)
        p = self._get_anon_profile()
        p.online_status_public = True
        p.last_activity_date = now
        self.assertFalse(p.is_online())

    def test_get_online_users_queryset(self):

        # Create some test users
        user1 = get_user_model().objects.create_user(username='johndoe',
                                                     password='illpassword',
                                                     email='john.doe@example.com')
        user2 = get_user_model().objects.create_user(username='johndoe2',
                                                     password='illpassword',
                                                     email='john.doe2@example.com')
        user3 = get_user_model().objects.create_user(username='johndoe3',
                                                     password='illpassword',
                                                     email='john.doe3@example.com')
        user4 = get_user_model().objects.create_user(username='johndoe4',
                                                     password='illpassword',
                                                     email='john.doe4@example.com')

        # Populate user profile for three of them
        user1_profile = user1.user_profile
        user2_profile = user2.user_profile
        user3_profile = user3.user_profile

        # Populate last activity date for two of them
        now = timezone.now()
        user2_profile.last_activity_date = now
        user3_profile.last_activity_date = now

        # Hidden online status of one user for testing
        user3_profile.online_status_public = False

        # Save changes before testing
        user2_profile.save()
        user3_profile.save()

        # Get the list of online user
        online_users = get_online_users_queryset().all()
        online_users = [user.id for user in online_users]

        # Check result
        self.assertEqual(len(online_users), 1)
        self.assertIn(user2_profile.user_id, online_users)

    def test_profile_updated_signal(self):
        """
        Test the "profile updated" signal emission.
        """
        p = self._get_anon_profile()
        signal_received = False
        received_user_profile = None

        def _signal_listener(sender, user_profile, **kwargs):
            nonlocal signal_received, received_user_profile
            signal_received = True
            received_user_profile = user_profile
        user_profile_updated.connect(_signal_listener)

        p.signature = 'Test'
        p.save()
        self.assertTrue(signal_received)
        self.assertEqual(received_user_profile, p)

    def test_get_subscribers_for_newsletter(self):

        # Create some test users
        user1 = get_user_model().objects.create_user(username='johndoe',
                                                     password='illpassword',
                                                     email='john.doe@example.com')
        user2 = get_user_model().objects.create_user(username='johndoe2',
                                                     password='illpassword',
                                                     email='john.doe2@example.com')
        user3 = get_user_model().objects.create_user(username='johndoe3',
                                                     password='illpassword',
                                                     email='john.doe3@example.com')

        # Populate user profile for three of them
        user1_profile = user1.user_profile
        user1_profile.accept_newsletter = True
        user1_profile.save()
        user2_profile = user2.user_profile
        user2_profile.accept_newsletter = True
        user2_profile.save()
        user3_profile = user3.user_profile
        user3_profile.accept_newsletter = False
        user3_profile.save()

        # Get the list of subscribers
        subscribers = UserProfile.objects.get_subscribers_for_newsletter()
        subscribers = [user.user_id for user in subscribers]

        # Check result
        self.assertEqual(len(subscribers), 2)
        self.assertIn(user1_profile.user_id, subscribers)
        self.assertIn(user2_profile.user_id, subscribers)
