"""
Middleware for the user accounts app.
"""

from django.utils import timezone

from .models import UserProfile


class LastActivityDateUpdateMiddleware(object):
    """
    Middleware for updating the "last activity date" of authenticated users.
    """

    def process_request(self, request):
        """
        Process the request, update the last activity date of current user if logged-in.
        :param request: The current request instance.
        """

        # Only handle authenticated users
        current_user = request.user
        if current_user.is_authenticated():

            # Update last login IP address
            now = timezone.now()
            updated = UserProfile.objects.filter(user=current_user).update(last_activity_date=now)
            if not updated:
                # The user profile does not exist yet. Fallback to a simple "get then save" logic.
                user_profile = current_user.user_profile
                user_profile.last_activity_date = now
                user_profile.save_no_rendering(update_fields=('last_activity_date',))
