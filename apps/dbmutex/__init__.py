"""
Database mutex app.

This reusable Django application provide low-level API for locking multiple parallel processes
 using mutex stored in the database.
"""

# Friendly import
from .engine import MutexLock
from .exceptions import Error, LockError, UnlockError, AlreadyLockedError, NoLockError, LockTimeoutError

default_app_config = 'apps.dbmutex.apps.DatabaseMutexConfig'
