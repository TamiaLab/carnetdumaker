"""
Forms for the forum app.
"""

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from apps.txtrender.forms import MarkupCharField
from apps.contentreport.forms import ContentReportCreationForm
from apps.tools.http_utils import get_client_ip_address

from .models import (ForumThread,
                     ForumThreadPost,
                     ForumThreadSubscription,
                     ForumUserProfile)
from .notifications import (notify_of_new_thread_post,
                            notify_of_new_forum_thread)


class ForumThreadCreationForm(forms.Form):
    """
    Forum's thread creation form.
    """

    title = forms.CharField(widget=forms.TextInput,
                            max_length=255,
                            label=_('Title'))

    content = MarkupCharField(label=_('Content'))

    closed = forms.BooleanField(widget=forms.CheckboxInput,
                                label=_('Closed'),
                                required=False)

    resolved = forms.BooleanField(widget=forms.CheckboxInput,
                                  label=_('Resolved'),
                                  required=False)

    notify_of_reply = forms.BooleanField(widget=forms.CheckboxInput,
                                         label=_('Notify me of new reply'),
                                         required=False)

    def save(self, request, parent_forum, author):
        """
        Save the new thread.
        :param request: The current request.
        :param parent_forum: The parent forum.
        :param author: The current user, to be used has thread's author.
        :return: The new thread object.
        """

        # Create the new thread and first post
        new_thread = ForumThread.objects.create_thread(parent_forum=parent_forum,
                                                       title=self.cleaned_data['title'],
                                                       author=author,
                                                       pub_date=timezone.now(),
                                                       content=self.cleaned_data['content'],
                                                       author_ip_address=get_client_ip_address(request),
                                                       closed=self.cleaned_data['closed'],
                                                       resolved=self.cleaned_data['resolved'])

        # Handle attachments
        # self.handle_new_attachments(new_thread.first_post)

        # Add subscriber if necessary
        if self.cleaned_data['notify_of_reply']:
            ForumThreadSubscription.objects.subscribe_to_thread(author, new_thread)

        # Notify subscribers
        notify_of_new_forum_thread(new_thread, request, author)

        # Return the newly created object
        return new_thread


class ForumThreadEditionForm(forms.ModelForm):
    """
    Forum's thread edition form.
    """

    content = MarkupCharField(label=_('Content'))

    class Meta:
        model = ForumThread
        fields = ('title', 'closed', 'resolved')

    def __init__(self, *args, **kwargs):
        super(ForumThreadEditionForm, self).__init__(*args, **kwargs)

        # Pre-fill content field
        first_post = self.instance.first_post
        self.fields['content'].initial = first_post.content

        # Display current attachments
        # self.add_attachment_fields(first_post)

    def clean(self):
        """
        Clean all form's fields.
        """
        # self.do_clean_attachments(self.instance.first_post)
        return super(ForumThreadEditionForm, self).clean()

    def save(self, *args, **kwargs):
        """
        Save the model instance related to this form.
        :param request: The current request.
        :param author: The current user, to be use as author (of the modification).
        :param args: Extra arguments for super()
        :param kwargs: Extra keyword arguments for super()
        :return: None
        """
        request = kwargs.pop('request', None)
        author = kwargs.pop('author', None)
        instance = super(ForumThreadEditionForm, self).save(*args, **kwargs)

        # Avoid oops
        assert request is not None
        assert author is not None

        # Handle deleted attachments
        first_post = instance.first_post
        # self.handle_deleted_attachments(first_post)

        # Handle new attachments
        # self.handle_new_attachments(first_post)

        # Save the first post's content
        first_post.content = self.cleaned_data['content']
        if first_post.author == author:
            # Update IP address if the original author edit the post
            # If another user edit the post (moderator, admin, ...), IP is not altered.
            first_post.author_ip_address = get_client_ip_address(request)
        first_post.save(current_user=author)


class ForumThreadDeleteForm(forms.Form):
    """
    Deletion confirmation form for a thread.
    """

    confirm = forms.BooleanField(widget=forms.CheckboxInput,
                                 label=_('I really want to delete this thread'),
                                 error_messages={'required': _('You must check the box to confirm the deletion.')})

    def save(self, thread):
        """
        Delete (logical delete) the thread.
        :param thread: The thread to be deleted.
        :return: None
        """
        thread.deleted_at = timezone.now()
        thread.save()


class ForumThreadReplyForm(forms.Form):
    """
    Forum's thread reply form.
    """

    content = MarkupCharField(label=_('Content'))

    notify_of_reply = forms.BooleanField(widget=forms.CheckboxInput,
                                         label=_('Notify me of new reply'),
                                         required=False)

    def save(self, request, parent_thread, author):
        """
        Save the new post.
        :param request: The current request.
        :param parent_thread: The parent thread instance.
        :param author: The current user, to be used as post's author.
        :return: The newly created post instance.
        """

        # Create the post
        new_post = ForumThreadPost.objects.create(parent_thread=parent_thread,
                                                  author=author,
                                                  content=self.cleaned_data['content'],
                                                  author_ip_address=get_client_ip_address(request))

        # Handle attachments
        # self.handle_new_attachments(new_post)

        # Add subscriber if necessary
        if self.cleaned_data['notify_of_reply']:
            ForumThreadSubscription.objects.subscribe_to_thread(author, parent_thread)
        else:
            ForumThreadSubscription.objects.unsubscribe_from_thread(author, parent_thread)

        # Notify subscribers
        notify_of_new_thread_post(new_post, request, author)

        # Return the newly created post object
        return new_post


class ForumThreadPostEditForm(forms.ModelForm):
    """
    Forum post edit form. Do NOT use this form for the first post of a thread!
    """

    class Meta:
        model = ForumThreadPost
        fields = ('content',)

    def __init__(self, *args, **kwargs):
        super(ForumThreadPostEditForm, self).__init__(*args, **kwargs)

        # Display current attachments
        # self.add_attachment_fields(self.instance)

    def clean(self):
        """
        Clean all form's fields.
        """
        # self.do_clean_attachments(self.instance)
        return super(ForumThreadPostEditForm, self).clean()

    def save(self, *args, **kwargs):
        """
        Save the form and related model.
        :param request: The current request.
        :param author: The current user, to be used as post's author.
        :param args: Any arguments for super()
        :param kwargs: Any keyword arguments for super()
        :return: None
        """
        request = kwargs.pop('request', None)
        author = kwargs.pop('author', None)
        post = super(ForumThreadPostEditForm, self).save(commit=False)

        # Avoid oops
        assert request is not None
        assert author is not None

        # Handle deleted attachments
        # self.handle_deleted_attachments(post)

        # Handle new attachments
        # self.handle_new_attachments(post)

        # Manual update of runtime fields
        post.last_modification_by = author
        if post.author == author:
            # Update IP address if the original author edit the post
            # If another user edit the post (moderator, admin, ...), IP is not altered.
            post.author_ip_address = get_client_ip_address(request)

        # Save the model
        post.save(current_user=author)
        self.save_m2m()


class ForumThreadPostDeleteForm(forms.Form):
    """
    Deletion confirmation form for a post.
    """

    confirm = forms.BooleanField(widget=forms.CheckboxInput,
                                 label=_('I really want to delete this post'),
                                 error_messages={'required': _('You must check the box to confirm the deletion.')})

    def save(self, post):
        """
        Delete (logical delete) the post.
        :param post: The post to be deleted.
        :return: None
        """
        post.deleted_at = timezone.now()
        post.save()


class ForumThreadPostReportForm(ContentReportCreationForm):
    """
    Form for reporting inadequate forum's post.
    """

    def get_extra_notification_kwargs(self):
        """
        Return extra arguments for the notification template.
        """
        return {
            'content_object_name': 'post',
            'title_template_name': "forum/thread_post_report_subject.txt",
            'message_template_name': "forum/thread_post_report_body.txt",
            'message_template_name_html': "forum/thread_post_report_body.html",
        }


class ForumProfileModificationForm(forms.ModelForm):
    """
    Forum user's account modification form.
    """

    class Meta:

        model = ForumUserProfile

        fields = ('notify_of_reply_by_default',)
