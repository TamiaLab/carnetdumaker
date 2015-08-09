"""
Tests suite for the admin views of the database mutex app.
"""

from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from ..models import DbMutexLock


class DbMutexLockAdminTestCase(TestCase):
    """
    Tests suite for the admin views.
    """

    def setUp(self):
        """
        Create some fixtures for the tests.
        """
        get_user_model().objects.create_superuser(username='johndoe',
                                                  password='illpassword',
                                                  email='john.doe@example.com')
        self.mutex = DbMutexLock.objects.create(mutex_name='test')

    def test_mutex_list_view_available(self):
        """
        Test the availability of the "mutex list" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:dbmutex_dbmutexlock_changelist'))
        self.assertEqual(response.status_code, 200)

    def test_mutex_edit_view_available(self):
        """
        Test the availability of the "edit mutex" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:dbmutex_dbmutexlock_change', args=[self.mutex.pk]))
        self.assertEqual(response.status_code, 200)
