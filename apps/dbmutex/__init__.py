"""
Database mutex app.

This reusable Django application provide low-level API for locking multiple parallel processes
 using mutex stored in the database.
"""

default_app_config = 'apps.dbmutex.apps.DatabaseMutexConfig'

# Friendly import
from .engine import MutexLock
