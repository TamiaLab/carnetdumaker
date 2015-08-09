"""
Forms for the content report app.
"""

from django import forms
from django.utils.translation import ugettext_lazy as _

from apps.tools.http_utils import get_client_ip_address

from .models import ContentReport


class ContentReportCreationForm(forms.Form):
    """
    ``ContentReport`` creation form for registered users only.
    """

    reason = forms.CharField(widget=forms.TextInput(),
                             max_length=255,
                             label=_('Reason'),
                             required=False)

    def save(self, request, content_obj, reporter):
        """
        Save the form by creating a new ``ContentReport`` for the given content object.
        :param request: The current request.
        :param content_obj: The related content instance.
        :param reporter: The author of this report.
        """

        # Create the report
        new_report = ContentReport.objects.create_report(content_object=content_obj,
                                                         reporter=reporter,
                                                         reporter_ip_address=get_client_ip_address(request),
                                                         reason=self.cleaned_data['reason'],
                                                         request=request,
                                                         extra_notification_kwargs=self.get_extra_notification_kwargs())

        # Return the newly created object
        return new_report

    def get_extra_notification_kwargs(self):
        """
        Return a dict of extra keywords arguments for the ``notify_of_new_report`` method, or None.
        """
        return None
