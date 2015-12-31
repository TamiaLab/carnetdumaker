"""
Tests suite for the data models of the user strike app.
"""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.test import TestCase
from django.utils import timezone

from ..models import UserStrike


class UserStrikeModelTestCase(TestCase):
    """
    Tests suite for the ``UserStrike`` data model class.
    """

    def _get_strike(self):
        """
        Creates some test fixtures.
        """
        author = get_user_model().objects.create_user(username='johndoe',
                                                      password='illpassword',
                                                      email='john.doe@example.com')
        user = get_user_model().objects.create_user(username='johnsmith',
                                                    password='illpassword',
                                                    email='john.smith@example.com')
        strike = UserStrike.objects.create(author=author,
                                           internal_reason='Test strike',
                                           target_user=user)
        return strike, author, user

    def test_default_values(self):
        """
        Test defaults value of a newly created strike.
        """
        strike, author, user = self._get_strike()
        self.assertIsNone(strike.target_ip_address)
        self.assertIsNotNone(strike.creation_date)
        self.assertIsNone(strike.expiration_date)
        self.assertEqual('', strike.public_reason)
        self.assertFalse(strike.block_access)

    def test_str_method(self):
        """
        Test the ``__str__`` method of the model for other tests.
        """
        strike, author, user = self._get_strike()
        self.assertEqual('Strike for "%s", reason: %s' % (strike.target_user.username,
                                                          strike.internal_reason), str(strike))

        strike.target_user = None
        strike.target_ip_address = '10.0.0.1'
        self.assertEqual('Strike for "%s", reason: %s' % (strike.target_ip_address,
                                                          strike.internal_reason), str(strike))

    def test_clean_target_user_or_ip_required(self):
        """
        Test if the model validation assert ``target_user`` or ``target_ip_address`` value.
        """
        strike, author, user = self._get_strike()

        with self.assertRaises(ValidationError) as e:
            strike.target_user = None
            strike.target_ip_address = None
            strike.full_clean()

    def test_search_for_strike_with_multiple_strike(self):
        """
        Test the ``search_for_strike`` method of the manager class with multiple strike.
        """
        author = get_user_model().objects.create_user(username='johndoe',
                                                      password='illpassword',
                                                      email='john.doe@example.com')
        user = get_user_model().objects.create_user(username='johnsmith',
                                                    password='illpassword',
                                                    email='john.smith@example.com')
        UserStrike.objects.create(author=author,
                                  internal_reason='Test strike 1',
                                  target_user=user,
                                  target_ip_address='10.0.0.42')
        strike = UserStrike.objects.create(author=author,
                                           internal_reason='Test strike 2',
                                           target_user=user,
                                           target_ip_address='10.0.0.42')
        result = UserStrike.objects.search_for_strike(user, '10.0.0.42')
        self.assertEqual(strike, result)

    def test_search_for_strike_with_multiple_strike_blocking_first(self):
        """
        Test the ``search_for_strike`` method of the manager class with multiple strike,
        asserting that blocking strike are processed first.
        """
        author = get_user_model().objects.create_user(username='johndoe',
                                                      password='illpassword',
                                                      email='john.doe@example.com')
        user = get_user_model().objects.create_user(username='johnsmith',
                                                    password='illpassword',
                                                    email='john.smith@example.com')
        strike = UserStrike.objects.create(author=author,
                                           internal_reason='Test strike 1',
                                           target_user=user,
                                           target_ip_address='10.0.0.42',
                                           block_access=True)
        UserStrike.objects.create(author=author,
                                  internal_reason='Test strike 2',
                                  target_user=user,
                                  target_ip_address='10.0.0.42')
        result = UserStrike.objects.search_for_strike(user, '10.0.0.42')
        self.assertEqual(strike, result)

    def test_search_for_strike_with_strike_expiration(self):
        """
        Test the ``search_for_strike`` method of the manager class with some expired strike.
        """
        now = timezone.now()
        past_now = now - timedelta(seconds=1)
        author = get_user_model().objects.create_user(username='johndoe',
                                                      password='illpassword',
                                                      email='john.doe@example.com')
        user = get_user_model().objects.create_user(username='johnsmith',
                                                    password='illpassword',
                                                    email='john.smith@example.com')
        UserStrike.objects.create(author=author,
                                  internal_reason='Test strike 1',
                                  target_user=user,
                                  target_ip_address='10.0.0.42',
                                  expiration_date=past_now)
        result = UserStrike.objects.search_for_strike(user, '10.0.0.42')
        self.assertIsNone(result)

    def test_search_for_strike_with_user(self):
        """
        Test the ``search_for_strike`` method of the manager class with just an user.
        """
        author = get_user_model().objects.create_user(username='johndoe',
                                                      password='illpassword',
                                                      email='john.doe@example.com')
        user = get_user_model().objects.create_user(username='johnsmith',
                                                    password='illpassword',
                                                    email='john.smith@example.com')
        strike = UserStrike.objects.create(author=author,
                                           internal_reason='Test strike 1',
                                           target_user=user)
        UserStrike.objects.create(author=author,
                                  internal_reason='Test strike 2',
                                  target_user=author,
                                  target_ip_address='10.0.0.42')
        result = UserStrike.objects.search_for_strike(user, None)
        self.assertEqual(strike, result)
        result = UserStrike.objects.search_for_strike(user, '192.168.1.5')
        self.assertEqual(strike, result)

    def test_search_for_strike_with_ip_address(self):
        """
        Test the ``search_for_strike`` method of the manager class with just an ip address.
        """
        author = get_user_model().objects.create_user(username='johndoe',
                                                      password='illpassword',
                                                      email='john.doe@example.com')
        user = get_user_model().objects.create_user(username='johnsmith',
                                                    password='illpassword',
                                                    email='john.smith@example.com')
        strike = UserStrike.objects.create(author=author,
                                           internal_reason='Test strike 1',
                                           target_ip_address='10.0.0.2')
        UserStrike.objects.create(author=author,
                                  internal_reason='Test strike 2',
                                  target_user=author,
                                  target_ip_address='10.0.0.42')
        result = UserStrike.objects.search_for_strike(None, '10.0.0.2')
        self.assertEqual(strike, result)
        result = UserStrike.objects.search_for_strike(user, '10.0.0.2')
        self.assertEqual(strike, result)

    def test_search_for_strike_with_user_and_ip_address(self):
        """
        Test the ``search_for_strike`` method of the manager class with an user and an IP address.
        """
        author = get_user_model().objects.create_user(username='johndoe',
                                                      password='illpassword',
                                                      email='john.doe@example.com')
        user = get_user_model().objects.create_user(username='johnsmith',
                                                    password='illpassword',
                                                    email='john.smith@example.com')
        strike = UserStrike.objects.create(author=author,
                                           internal_reason='Test strike 1',
                                           target_user=user,
                                           target_ip_address='10.0.0.2')
        result = UserStrike.objects.search_for_strike(user, '10.0.0.2')
        self.assertEqual(strike, result)

    def test_search_for_strike_with_user_and_ip_address_separate(self):
        """
        Test the ``search_for_strike`` method of the manager class with a separated user and an IP address.
        """
        author = get_user_model().objects.create_user(username='johndoe',
                                                      password='illpassword',
                                                      email='john.doe@example.com')
        user = get_user_model().objects.create_user(username='johnsmith',
                                                    password='illpassword',
                                                    email='john.smith@example.com')
        UserStrike.objects.create(author=author,
                                  internal_reason='Test strike 1',
                                  target_user=user,)
        strike2 = UserStrike.objects.create(author=author,
                                            internal_reason='Test strike 2',
                                            target_ip_address='10.0.0.2')
        result = UserStrike.objects.search_for_strike(user, '10.0.0.2')
        self.assertEqual(strike2, result)

    def test_search_for_strike_with_nothing(self):
        """
        Test the ``search_for_strike`` method of the manager class with no user nor ip address.
        """
        self.assertIsNone(UserStrike.objects.search_for_strike(None, None))
