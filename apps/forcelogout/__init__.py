"""
Force logout app.

This reusable Django application allow administrators to force a specific user to log out from any active sessions.
This application also provide an API to force logout by software from another application.
"""

default_app_config = 'apps.forcelogout.apps.ForceLogoutConfig'
