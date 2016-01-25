"""
Data models managers for the redirect app.
"""

from django.db import models
from django.conf import settings


class RedirectionManager(models.Manager):
    """
    Manager class for the ``Redirection`` data model.
    """

    def get_redirection(self, current_site, request):
        """
        Get the redirection for the given path.
        :param current_site: The current site object.
        :param request: The current request.
        :return: The redirection for the given path or None.
        """

        # Query the raw path
        try:
            return self.get(
                    site=current_site,
                    old_path=request.get_full_path(),
                    active=True
            )
        except self.model.DoesNotExist:
            pass

        # Handle URL without ending slash
        if settings.APPEND_SLASH and not request.path.endswith('/'):
            try:
                return self.get(
                        site=current_site,
                        old_path=request.get_full_path(force_append_slash=True),
                        active=True
                )
            except self.model.DoesNotExist:
                pass

        # No redirection found
        return None
