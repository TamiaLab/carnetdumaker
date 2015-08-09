"""
Sitemap for the bug tracker app.
"""

from django.contrib.sitemaps import Sitemap

from .models import IssueTicket


class IssueTicketsSitemap(Sitemap):
    """
    Sitemap for the bug tracker.
    """

    changefreq = 'weekly'
    priority = 0.2

    def items(self):
        """
        Return all the tickets.
        :return: All the tickets.
        """
        return IssueTicket.objects.all()

    def lastmod(self, obj):
        """
        Return the last modification date of the given ticket.
        :param obj: The ticket.
        :return: The last modification date of the given ticket.
        """
        return obj.last_modification_date
