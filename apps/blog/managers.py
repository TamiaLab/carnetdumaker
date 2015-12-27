"""
Objects managers for the blog app.
"""

from django.db import models
from django.db.models import Q
from django.utils import timezone

from .constants import ARTICLE_STATUS_PUBLISHED


class ArticleManager(models.Manager):
    """
    Manager class for the ``Article`` data model.
    """

    use_for_related_fields = True

    def published(self):
        """
        Return a queryset with all currently published articles ordering from the most recent to the less recent.
        Visible articles are determined using a three steps process:
        - status must be 'published',
        - published date must be before now, or now,
        - if expiration date is set, the expiration date must be after now, or now.
        :return: A queryset with all currently published article.
        """
        now = timezone.now()
        return self.filter(Q(expiration_date__isnull=True) |
                           Q(expiration_date__isnull=False,
                             expiration_date__gte=now),
                           pub_date__lte=now,
                           status=ARTICLE_STATUS_PUBLISHED) \
            .order_by('-featured', '-pub_date')

    def network_publishable(self):
        """
        Return a queryset with all article currently published and flagged for network publication.
        """
        return self.published().filter(network_publish=True)

    def published_per_month(self):
        """
        Return a sorted array of tuples like ``(year, ((month, count),))``. This tuple is a summary of all published
        articles by month and year.
        WARNING: DATABASE DEPENDENT CODE HERE!
        """
        # This is ONLY PostgreSQL compatible.
        #
        # For MySQL use:
        # 'year': "YEAR(pub_date)"
        # 'month': "MONTH(pub_date)"

        # Get the raw archives stats as tuple (year, month, count)
        archives = self.published().extra({'year': "EXTRACT(YEAR FROM pub_date)",
                                           'month': "EXTRACT(MONTH FROM pub_date)"}) \
            .values_list('year', 'month')

        # Turn archives into something useful like a dict {year: {month: count}}
        archive_calendar = {}
        for year, month in archives:

            # Fix float value (need int)
            year = int(year)
            month = int(month)

            # Store value
            if year in archive_calendar:
                if month in archive_calendar[year]:
                    archive_calendar[year][month] += 1
                else:
                    archive_calendar[year][month] = 1
            else:
                archive_calendar[year] = {month: 1}

        # Sort month of each year
        for year, months in archive_calendar.items():
            archive_calendar[year] = sorted(list(months.items()), key=lambda x: x[0])

        # Then, sort year
        return sorted(list(archive_calendar.items()), key=lambda x: x[0])
