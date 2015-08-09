"""
Test suite for the views of the registration app.
"""

from django.test import SimpleTestCase, Client
from django.core.urlresolvers import reverse


class RegistrationViewsTestCase(SimpleTestCase):
    """
    Test suite for the views.
    """

    def test_registration_closed_view_available(self):
        """
        Test the availability of the "registration closed" view.
        """
        client = Client()
        response = client.get(reverse('registration:registration_closed'))
        self.assertEqual(response.status_code, 200)

    def test_registration_register_view_available(self):
        """
        Test the availability of the "registration" view.
        """
        client = Client()
        response = client.get(reverse('registration:registration_register'))
        self.assertEqual(response.status_code, 200)

    def test_registration_done_view_available(self):
        """
        Test the availability of the "registration done" view.
        """
        client = Client()
        response = client.get(reverse('registration:registration_done'))
        self.assertEqual(response.status_code, 200)

    def test_registration_activate_view_available(self):
        """
        Test the availability of the "account activation" view. Used dummy activation data to test availability.
        """
        client = Client()
        response = client.get(reverse('registration:registration_activate',
                                      kwargs={'uidb64': 1, 'activation_key': 'TESTERCESTDOUTER'}))
        self.assertEqual(response.status_code, 200)

    def test_registration_complete_view_available(self):
        """
        Test the availability of the "registration complete" view.
        """
        client = Client()
        response = client.get(reverse('registration:registration_complete'))
        self.assertEqual(response.status_code, 200)
