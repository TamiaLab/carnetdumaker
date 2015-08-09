"""
Tests suite for the database mutex app.
"""

from unittest import mock
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from ..settings import MUTEX_LOCK_EXPIRATION_DELAY_SEC
from ..models import DbMutexLock


class DatabaseMutexTestCase(TestCase):
    """
    Tests suite for the database mutex app.
    """

    def test_str_method(self):
        """
        Test the ``__str__`` method of the ``DbMutexLock`` class.
        """
        mutex = DbMutexLock.objects.create(mutex_name='test')
        self.assertEqual("Mutex %s" % mutex.mutex_name, str(mutex))

    def test_expired_method(self):
        """
        Test the ``expired()`` method of the ``DbMutexLock`` class.
        """
        now = timezone.now()
        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = now
            mutex = DbMutexLock.objects.create(mutex_name='test')
            self.assertFalse(mutex.expired())

        future_now = now + timedelta(seconds=MUTEX_LOCK_EXPIRATION_DELAY_SEC - 1)
        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = future_now
            self.assertFalse(mutex.expired())

        future_now = now + timedelta(seconds=MUTEX_LOCK_EXPIRATION_DELAY_SEC)
        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = future_now
            self.assertTrue(mutex.expired())

    def test_ordering(self):
        """
        Test the default ordering of the lock.
        """
        DbMutexLock.objects.create(mutex_name='test1')
        DbMutexLock.objects.create(mutex_name='test2')

        # Test the ordering
        queryset = DbMutexLock.objects.all()
        self.assertQuerysetEqual(queryset, ['<DbMutexLock: Mutex test2>', '<DbMutexLock: Mutex test1>'])
