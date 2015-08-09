"""
Data models managers for the bug tracker app.
"""

from django.db import models


class IssueTicketSubscriptionManager(models.Manager):
    """
    Manager class for the ``IssueTicketSubscription`` data model.
    """

    def get_subscribers_for_issue(self, issue):
        """
        Get all active subscribers for the given issue.
        :param issue: The target issue.
        :return: A queryset of all active subscribers for the given issue.
        """
        return self.filter(issue=issue, active=True)

    def has_subscribed_to_issue(self, user, issue):
        """
        Check if the given user has subscribed to the given issue, or not.
        :param user: The user to check.
        :param issue: The issue to check.
        :return: ``True`` if the user has subscribed to the given issue, ``False`` otherwise.
        """
        return self.filter(user=user, issue=issue, active=True).exists()

    def subscribe_to_issue(self, user, issue):
        """
        Subscribe to the given issue.
        :param user: The subscriber.
        :param issue: The issue to subscribe for.
        :return: None
        """
        subscription, created = self.get_or_create(user=user, issue=issue)
        if not created:
            subscription.active = True
            subscription.save()

    def unsubscribe_from_issue(self, user, issue):
        """
        Unsubscribe from the given issue.
        :param user: The un-subscriber.
        :param issue: The issue to subscribe for.
        :return: None
        """
        self.filter(user=user, issue=issue).update(active=False)


class BugTrackerUserProfileManager(models.Manager):
    """
    Manager class for the ``BugTrackerUserProfile`` data model.
    """

    def get_subscribers_for_new_issue(self):
        """
        Get all subscribers for new issue.
        :return: A queryset of all subscribers for new issue.
        """
        return self.filter(notify_of_new_issue=True)
