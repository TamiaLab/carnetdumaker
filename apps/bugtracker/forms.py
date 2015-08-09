"""
Forms for the bug tracker app.
"""

from django import forms
from django.utils.translation import ugettext_lazy as _

from apps.txtrender.forms import MarkupCharField
from apps.contentreport.forms import ContentReportCreationForm
from apps.tools.http_utils import get_client_ip_address

from .models import (IssueTicket,
                     IssueTicketSubscription,
                     IssueComment,
                     BugTrackerUserProfile)
from .notifications import (notify_of_new_comment,
                            notify_of_new_issue)


class IssueTicketCreationForm(forms.Form):
    """
    ``IssueTicket`` creation form for registered users only.
    """

    title = forms.CharField(widget=forms.TextInput(),
                            max_length=255,
                            label=_('Title'))

    description = MarkupCharField(label=_('Problem description'))

    notify_of_reply = forms.BooleanField(widget=forms.CheckboxInput(),
                                         label=_('Notify me of new reply'),
                                         required=False)

    def save(self, request, submitter):
        """
        Save the form by creating a new ``IssueTicket``.
        :param request: The current request.
        :param submitter: The ticket's submitter.
        :return The newly created ticket.
        """
        new_obj = IssueTicket.objects.create(title=self.cleaned_data['title'],
                                             description=self.cleaned_data['description'],
                                             submitter=submitter,
                                             submitter_ip_address=get_client_ip_address(request))

        # Add subscriber if necessary
        if self.cleaned_data['notify_of_reply']:
            IssueTicketSubscription.objects.subscribe_to_issue(submitter, new_obj)

        # Notify subscribers
        notify_of_new_issue(new_obj, request, submitter)

        # Return the newly created object
        return new_obj


class IssueTicketEditionForm(forms.ModelForm):
    """
    ``IssueTicket`` edition form for registered users only.
    """

    class Meta:
        model = IssueTicket

        fields = ('title',
                  'description')


class IssueCommentCreationForm(forms.Form):
    """
    ``IssueComment`` creation form for registered users only.
    """

    comment_body = MarkupCharField(label=_('Comment text'))

    notify_of_reply = forms.BooleanField(widget=forms.CheckboxInput(),
                                         label=_('Notify me of new reply'),
                                         required=False)

    def save(self, request, issue, author):
        """
        Save the form by creating a new ``IssueComment`` for the given ``IssueTicket``.
        Drop a success flash message after saving.
        :param request: The current request.
        :param issue: The related issue instance.
        :param author: The author of this comment.
        """
        new_obj = IssueComment.objects.create(issue=issue,
                                              author=author,
                                              body=self.cleaned_data['comment_body'],
                                              author_ip_address=get_client_ip_address(request))

        # Add subscriber if necessary
        if self.cleaned_data['notify_of_reply']:
            IssueTicketSubscription.objects.subscribe_to_issue(author, new_obj.issue)
        else:
            IssueTicketSubscription.objects.unsubscribe_from_issue(author, new_obj.issue)

        # Notify subscribers
        notify_of_new_comment(issue, new_obj, request, author)

        # Return the newly created object
        return new_obj


class IssueCommentReportCreationForm(ContentReportCreationForm):
    """
    ``IssueCommentReport`` creation form for registered users only.
    """

    def get_extra_notification_kwargs(self):
        """
        Return extra arguments for the notification template.
        """
        return {
            'content_object_name': 'comment',
            'title_template_name': "bugtracker/issue_comment_report_subject.txt",
            'message_template_name': "bugtracker/issue_comment_report_body.txt",
            'message_template_name_html': "bugtracker/issue_comment_report_body.html",
        }


class BugTrackerProfileModificationForm(forms.ModelForm):
    """
    Bug tracker user's account modification form.
    """

    class Meta:
        model = BugTrackerUserProfile

        fields = ('notify_of_new_issue',
                  'notify_of_reply_by_default')
