"""
Data models managers for the user strike app.
"""

from django.db import models
from django.db.models import Q
from django.utils import timezone


class UserStrikeManager(models.Manager):
    """
    Manager class for the ``UserStrike`` data model.
    """

    use_for_related_fields = True

    def search_for_strike(self, user, ip_address):
        """
        Search the latest (non expired) strike for the given user or IP address.
        :param user: The user instance to search strike for.
        :param ip_address: The IP address to search strike for.
        """

        # Compute the lookup expression
        if not user and not ip_address:
            return None
        elif user and not ip_address:
            strike_lookup = Q(target_user=user)
        elif not user and ip_address:
            strike_lookup = Q(target_ip_address=ip_address)
        else:
            strike_lookup = Q(target_user=user) | Q(target_ip_address=ip_address)

        # Do the search
        return self.filter(Q(expiration_date__isnull=True) | Q(expiration_date__isnull=False,
                                                               expiration_date__gte=timezone.now()),
                           strike_lookup).order_by('-block_access', '-creation_date').first()
