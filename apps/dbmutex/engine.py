"""
Engine class for the database mutex app.
"""

from datetime import timedelta

from django.db import transaction, IntegrityError
from django.utils import timezone

from .models import DbMutexLock
from .settings import MUTEX_LOCK_EXPIRATION_DELAY_SEC
from .exceptions import (AlreadyLockedError,
                         NoLockError,
                         LockTimeoutError)


class MutexLock(object):
    """
    An object that acts as a context manager for acquiring a database mutex lock.
    """

    def __init__(self, mutex_name):
        """
        This context manager can be used in the following way:
        .. code-block:: python
            from apps.dbmutex import MutexLock, AlreadyLockedError, LockTimeoutError

            # Lock a critical section of code
            try:
                with MutexLock('mutex_name'):
                    # Run critical code here
                    pass
            except AlreadyLockedError:
                print('Could not obtain lock')
            except LockTimeoutError:
                print('Task completed but the lock timed out')

        :param mutex_name: The name of the lock to be acquired (or at least, try to be).
        """
        self.mutex_name = mutex_name
        self.lock = None

    @staticmethod
    def delete_expired_locks():
        """
        Deletes all expired mutex locks if a ttl is provided.
        """
        if MUTEX_LOCK_EXPIRATION_DELAY_SEC:
            deletion_threshold = timezone.now() - timedelta(seconds=MUTEX_LOCK_EXPIRATION_DELAY_SEC)
            DbMutexLock.objects.filter(creation_date__lte=deletion_threshold).delete()

    def __enter__(self):
        self.acquire()

    def __exit__(self, *args):
        self.release()

    def acquire(self):
        """
        Acquires the mutex lock. Takes the necessary steps to delete any stale locks.
        Throws a AlreadyLockedError if the mutex can't be acquired.
        """

        # Delete any expired locks first
        self.delete_expired_locks()

        # Try to create the lock
        try:
            with transaction.atomic():
                self.lock = DbMutexLock.objects.create(mutex_name=self.mutex_name)
        except IntegrityError:
            self.lock = None
            raise AlreadyLockedError('Could not acquire lock "{0}" (already locked)'.format(self.mutex_name))

    def release(self):
        """
        Releases the mutex lock. Throws a LockTimeoutError if the lock was released before the function finished.
        Throws a NoLockError if the lock has never been acquired.
        """

        # Assert lock is acquired
        if not self.lock:
            raise NoLockError('Lock {0} has never been acquired'.format(self.mutex_name))

        # Test if the lock has expired (just for detecting misconfiguration problem during debug)
        if self.lock.expired():
            raise LockTimeoutError('Lock {0} expired before function completed'.format(self.mutex_name))
        else:
            self.lock.delete()
