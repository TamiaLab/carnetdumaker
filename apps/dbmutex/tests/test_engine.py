"""
Tests suite for the engine of the database mutex app.
"""

from datetime import timedelta
from unittest import mock

from django.test import TestCase
from django.utils import timezone

from .. import MutexLock
from ..exceptions import AlreadyLockedError, NoLockError, LockTimeoutError
from ..settings import MUTEX_LOCK_EXPIRATION_DELAY_SEC
from ..models import DbMutexLock


class DatabaseMutexEngineTestCase(TestCase):
    """
    Tests suite for the engine of the database mutex app.
    """

    def test_mutex_acquire(self):
        """
        Test if the same lock can be acquire multiple time in normal situation.
        """
        self.assertEqual(DbMutexLock.objects.count(), 0)
        with MutexLock('test'):
            self.assertTrue(True)
            self.assertEqual(DbMutexLock.objects.count(), 1)

        self.assertEqual(DbMutexLock.objects.count(), 0)
        with MutexLock('test'):
            self.assertTrue(True)
            self.assertEqual(DbMutexLock.objects.count(), 1)

    def test_mutex_multiple_acquire(self):
        """
        Test if the lock can be acquire when multiple process require the lock at the same time.
        """
        lock = MutexLock('test')
        lock.acquire()

        with self.assertRaises(AlreadyLockedError):
            with MutexLock('test'): # Should fail
                self.assertTrue(False)

        # The first lock should still exist
        self.assertTrue(DbMutexLock.objects.filter(mutex_name='test').exists())

    def test_mutex_never_acquired(self):
        """
        Test if the ``release()`` method throws the ``NoLockError`` when the lock is never been acquired.
        """
        lock = MutexLock('test')
        with self.assertRaises(NoLockError):
            lock.release() # Should fail

    def test_mutex_acquire_after_timeout(self):
        """
        Test if the lock can be acquire after the timeout delay.
        """
        lock = MutexLock('test')
        lock.acquire()

        future_now = timezone.now() + timedelta(seconds=MUTEX_LOCK_EXPIRATION_DELAY_SEC)
        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = future_now
            with MutexLock('test'):  # Should work
                pass

    def test_multiple_mutex_work(self):
        """
        Test if multiple different mutex work together without interacting.
        """
        self.assertEqual(DbMutexLock.objects.count(), 0)
        with MutexLock('test'):
            self.assertEqual(DbMutexLock.objects.count(), 1)
            with MutexLock('test2'):
                self.assertEqual(DbMutexLock.objects.count(), 2)
                with MutexLock('test3'):
                    self.assertEqual(DbMutexLock.objects.count(), 3)
                self.assertEqual(DbMutexLock.objects.count(), 2)
            self.assertEqual(DbMutexLock.objects.count(), 1)
        self.assertEqual(DbMutexLock.objects.count(), 0)

    def test_mutex_release_error_after_timeout(self):
        """
        Test if the ``release()`` method throws the ``LockTimeoutError`` when the lock has expired before releasing it.
        """
        lock = MutexLock('test')
        lock.acquire()
        future_now = timezone.now() + timedelta(seconds=MUTEX_LOCK_EXPIRATION_DELAY_SEC)
        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = future_now
            with self.assertRaises(LockTimeoutError):
                lock.release()

    def test_mutex_acquire_when_old_mutex_expired(self):
        """
        Test if it's possible to acquire a lock, previousely acquired and not relased, who have expired by now.
        """
        lock = MutexLock('test')
        lock.acquire()
        future_now = timezone.now() + timedelta(seconds=MUTEX_LOCK_EXPIRATION_DELAY_SEC)
        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = future_now
            self.assertEqual(DbMutexLock.objects.count(), 1)
            lock = MutexLock('test')
            lock.acquire()
            self.assertEqual(DbMutexLock.objects.count(), 1)
            lock.release()
            self.assertEqual(DbMutexLock.objects.count(), 0)
