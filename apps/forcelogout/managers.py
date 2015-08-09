"""
Objects manager for the force-logout app.
"""

from django.db.models import Manager
from django.utils import timezone


class ForceLogoutOrderManager(Manager):
    """
    Manager for the ``ForceLogoutOrder`` object class.
    """

    def force_logout(self, user):
        """
        Force the given user to be logout by creating a new logout order or updating a previous one.
        :param user: The user to be logout.
        :return: The created or updated logout order.
        """
        now = timezone.now()
        order, created = self.update_or_create(user=user, defaults={'order_date': now})
        return order
