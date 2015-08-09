"""
Data models managers for the content report app.
"""

from django.db import models

from .notifications import notify_of_new_report


class ContentReportManager(models.Manager):
    """
    Manager class for the ``ContentReport`` data model.
    """

    def create_report(self, content_object, reporter, reporter_ip_address, reason, request,
                      extra_notification_kwargs=None):
        """
        Create a new content report.
        :param content_object: The reported object.
        :param reporter: The reporting user.
        :param reporter_ip_address: the reporting user IP address.
        :param reason: The reporting reason (optional).
        :param request: The current request (for IP address and notifications).
        :param extra_notification_kwargs: Extra keyword arguments for the ``notify_of_new_report`` method.
        :return The newly create report.
        """

        # Create the report
        new_report = self.create(content_object=content_object,
                                 reporter=reporter,
                                 reason=reason,
                                 reporter_ip_address=reporter_ip_address)

        # Notify admins of the new report
        if extra_notification_kwargs is None:
            notify_of_new_report(new_report, reporter, request)
        else:
            notify_of_new_report(new_report, reporter, request, **extra_notification_kwargs)

        # Return the newly created report
        return new_report
