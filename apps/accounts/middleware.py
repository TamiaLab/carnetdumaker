"""
Middleware for the user accounts app.
"""

from django.utils import timezone


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
            # FIXME This generate two SQL requests per view. Maybe use update_or_create instead?
            user_profile = current_user.user_profile
            user_profile.last_activity_date = timezone.now()
            user_profile.save_no_rendering(update_fields=('last_activity_date',))
