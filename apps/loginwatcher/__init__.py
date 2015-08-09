"""
Log watcher app.

This reusable Django application hook all contrib.auth signal in order to store successful/failed
login attempt and logout of users. This allow monitoring of brute force attack or distributed user
targeting.
"""

default_app_config = 'apps.loginwatcher.apps.LogWatcherConfig'
