"""
Middleware for the user strike app.
"""

from django.utils import timezone
from django.contrib import messages
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _

from apps.tools.http_utils import get_client_ip_address

from .models import UserStrike


class UserStrikeMiddleware(object):
    """
    Middleware for blocking access to the website for banned users.
    """

    template_name = 'userstrike/access_blocked.html'

    def process_request(self, request):
        """
        Process the request, search for strike and do the job.
        :param request: The current request instance.
        """

        # Super admin cannot be kicked out
        if request.user.is_superuser:
            return

        # Search for strike
        current_user = request.user if request.user.is_authenticated() else None
        ip_address = get_client_ip_address(request)
        strike = UserStrike.objects.search_for_strike(user=current_user, ip_address=ip_address)

        # Test if strike found
        if strike and strike.block_access:

            # Block access to the website
            context = {
                'strike': strike,
            }
            return TemplateResponse(request, self.template_name, context, status=403)

        elif strike:

            # Warn user
            reason_msg = _('The reason of this warning is: "%s".') % strike.public_reason if strike.public_reason else ''
            expire_msg =  _('This warning will expire at %s.') % strike.expiration_date.isoformat(' ') if strike.expiration_date else _('This warning is not time limited.')
            messages.add_message(request, messages.WARNING,
                                 '%s\n%s\n%s' % (_('You have received a warning from an administrator.'),
                                       reason_msg, expire_msg),
                                 extra_tags='strike_warning', fail_silently=True)
