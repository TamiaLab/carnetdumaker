"""
Exceptions for the database mutex apps.
"""


class Error(RuntimeError):
    """
    This is the base class for all exceptions raised by the database mutex app.
    """
    pass


class LockError(Error):
    """
    This is the base class for all exceptions raised when attempting to lock a mutex.
    """
    pass


class UnlockError(Error):
    """
    This is the base class for all exceptions raised when attempting to unlock a mutex.
    """
    pass


class AlreadyLockedError(LockError):
    """
    This exception is raised if the MutexLock.acquire() detects a mutex is already locked.
    """
    pass


class NoLockError(UnlockError):
    """
    This exception is raised if the mutex has never been acquired.
    """
    pass


class LockTimeoutError(UnlockError):
    """
    This exception is raised if the mutex has expired before MutexLock.release() is called.
    """
    pass
