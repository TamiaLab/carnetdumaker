"""
Models for the bug tracker app.
"""

from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from apps.tools.models import ModelDiffMixin
from apps.tools.fields import AutoOneToOneField
from apps.txtrender.fields import RenderTextField
from apps.txtrender.utils import render_document
from apps.txtrender.signals import render_engine_changed

from .constants import (STATUS_CODES,
                        STATUS_OPEN,
                        PRIORITY_CODES,
                        PRIORITY_NEED_REVIEW,
                        DIFFICULTY_CODES,
                        DIFFICULTY_NORMAL)
from .managers import (IssueTicketSubscriptionManager,
                       BugTrackerUserProfileManager)
from .settings import (NB_ISSUE_COMMENTS_PER_PAGE,
                       NB_SECONDS_BETWEEN_COMMENTS)


class AppComponent(models.Model):
    """
    Bug tracker application component.
    An application component is made of:
    - a name for display,
    - a name for internal use (not displayed),
    - a description (no HTML here).
    """

    name = models.CharField(_('Name (for display)'),
                            max_length=255)

    internal_name = models.CharField(_('Name (for internal use)'),
                                     max_length=255)

    description = models.TextField(_('Description'),
                                   default='',
                                   blank=True)

    class Meta:
        verbose_name = _('Application component')
        verbose_name_plural = _('Application components')

    def __str__(self):
        return self.name


class IssueTicket(ModelDiffMixin, models.Model):
    """
    Bug issue ticket model.
    An issue ticket is made of:
    - a title,
    - a related app component,
    - a description of the problem (source and HTML version),
    - a submitter, submitted tickets are available in the User model using ``submitted_issues``.
    - a submitted date and last modified data (for filtering and keep trace of modifications),
    - a "assigned to" user in charge of the problem, assigned tickets are available in the User
    model using ``assigned_issues``. Auto set to null if user is deleted from database to avoid
    cascade deletion of all issues assigned to this user.
    - a status, default "open",
    - a priority, default "need review",
    - a difficulty, default "normal".
    """

    title = models.CharField(_('Title'),
                             max_length=255)

    component = models.ForeignKey(AppComponent,
                                  db_index=True,  # Database optimization
                                  related_name='tickets',
                                  default=None,
                                  blank=True,
                                  null=True,
                                  on_delete=models.SET_NULL)

    description = RenderTextField(_('Description'))

    description_html = models.TextField(_('Description (raw HTML)'))

    description_text = models.TextField(_('Description (raw text)'))

    submitter = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  db_index=True,  # Database optimization
                                  verbose_name=_('Submitter'),
                                  related_name="submitted_issues")

    submission_date = models.DateTimeField(_('Submission date'),
                                           db_index=True,  # Database optimization
                                           auto_now_add=True)

    last_modification_date = models.DateTimeField(_('Last modification date'),
                                                  db_index=True,  # Database optimization
                                                  auto_now=True)

    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL,
                                    db_index=True,  # Database optimization
                                    verbose_name=_('Assigned to'),
                                    related_name="assigned_issues",
                                    default=None,
                                    blank=True,
                                    null=True,
                                    on_delete=models.SET_NULL)

    status = models.CharField(_('Status'),
                              db_index=True,  # Database optimization
                              max_length=10,
                              default=STATUS_OPEN,
                              choices=STATUS_CODES)

    priority = models.CharField(_('Priority'),
                                db_index=True,  # Database optimization
                                max_length=10,
                                default=PRIORITY_NEED_REVIEW,
                                choices=PRIORITY_CODES)

    difficulty = models.CharField(_('Difficulty'),
                                  db_index=True,  # Database optimization
                                  max_length=10,
                                  default=DIFFICULTY_NORMAL,
                                  choices=DIFFICULTY_CODES)

    submitter_ip_address = models.GenericIPAddressField(_('Submitter IP address'),
                                                        default=None,
                                                        blank=True,
                                                        null=True)

    class Meta:
        verbose_name = _('Issue ticket')
        verbose_name_plural = _('Issue tickets')
        get_latest_by = 'submission_date'
        permissions = (
            ('allow_titles_in_ticket', 'Allow titles in issue ticket'),
            ('allow_alerts_box_in_ticket', 'Allow alerts box in issue ticket'),
            ('allow_text_colors_in_ticket', 'Allow coloured text in issue ticket'),
            ('allow_cdm_extra_in_ticket', 'Allow CDM extra in issue ticket'),
            ('allow_raw_link_in_ticket', 'Allow raw link (without forcing nofollow) in issue ticket'),

            ('allow_titles_in_comment', 'Allow titles in issue comment'),
            ('allow_alerts_box_in_comment', 'Allow alerts box in issue comment'),
            ('allow_text_colors_in_comment', 'Allow coloured text in issue comment'),
            ('allow_cdm_extra_in_comment', 'Allow CDM extra in issue comment'),
            ('allow_raw_link_in_comment', 'Allow raw link (without forcing nofollow) in issue comment'),
        )
        ordering = ('-submission_date', 'priority', 'status', 'title')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """
        Return the permalink to this issue.
        """
        return reverse('bugtracker:issue_detail', kwargs={'pk': self.pk})

    def get_edit_url(self):
        """
        Return the "edit" permalink for this issue.
        """
        return reverse('bugtracker:issue_edit', kwargs={'pk': self.pk})

    def get_subscribe_url(self):
        """
        Return the "subscribe" permalink to this issue.
        """
        return reverse('bugtracker:issue_subscribe', kwargs={'pk': self.pk})

    def get_unsubscribe_url(self):
        """
        Return the "unsubscribe" permalink to this issue.
        """
        return reverse('bugtracker:issue_unsubscribe', kwargs={'pk': self.pk})

    def get_latest_comments_rss_feed_url(self):
        """
        Return the permalink to "latest comments" RSS feed for this issue.
        """
        return reverse('bugtracker:latest_issue_comments_for_issue_rss', kwargs={'pk': self.pk})

    def get_latest_comments_atom_feed_url(self):
        """
        Return the permalink to "latest comments" Atom feed for this issue.
        """
        return reverse('bugtracker:latest_issue_comments_for_issue_rss', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        """
        Save the ticket.
        If the ticket already exist (ticket modification), add a new comment to list all modifications.
        Take three extra kwargs:
        - changes_comment: The comment text used to create the modification comment (default '').
        - changes_author: The user making the change (default self.submitter).
        - changes_author_ip_address: The IP address of the user (default None).
        - request: The current request, for notification.
        :param kwargs: super save() kwargs
        :param args: super save() args
        :return None
        """

        # Get extra arguments
        changes_comment = kwargs.pop('changes_comment', '')
        changes_author = kwargs.pop('changes_author', self.submitter)
        changes_author_ip_address = kwargs.pop('changes_author_ip_address', None)
        request = kwargs.pop('request', None)

        # Render description text
        self.render_description()

        # Detect ticket modifications
        changed_fields = self.diff
        has_changed = (self.pk and ('component' in changed_fields or
                                    'assigned_to' in changed_fields or
                                    'status' in changed_fields or
                                    'priority' in changed_fields or
                                    'difficulty' in changed_fields))

        # Fix User PK
        if 'assigned_to' in changed_fields:
            assigned_to = changed_fields['assigned_to']
            assigned_to_old = get_user_model().objects.get(pk=assigned_to[0]).username if assigned_to[0] else None
            assigned_to_new = get_user_model().objects.get(pk=assigned_to[1]).username if assigned_to[1] else None
            changed_fields['assigned_to'] = (assigned_to_old, assigned_to_new)

        # Fix component PK
        if 'component' in changed_fields:
            component = changed_fields['component']
            component_old = AppComponent.objects.get(pk=component[0]).internal_name if component[0] else None
            component_new = AppComponent.objects.get(pk=component[1]).internal_name if component[1] else None
            changed_fields['component'] = (component_old, component_new)

        # Important note: check for change BEFORE saving changes, then auto-comment, otherwise the PK will not exist
        super(IssueTicket, self).save(*args, **kwargs)

        # Create the change comment and history
        if has_changed:
            comment = IssueComment.objects.create(issue=self,
                                                  author=changes_author,
                                                  body=changes_comment,
                                                  author_ip_address=changes_author_ip_address)
            for field in ('component', 'assigned_to', 'status', 'priority', 'difficulty'):
                if field in changed_fields:
                    old_value, new_value = changed_fields[field]
                    IssueChange.objects.create(issue=self,
                                               comment=comment,
                                               field_name=field,
                                               old_value=str(old_value) or '',
                                               new_value=str(new_value) or '')
            if request is not None:
                self.notify_new_comment(comment, request)

    def notify_new_comment(self, comment, request):
        """
        Notify subscribers of a new comment. Overload this function to change default arguments.
        :param comment: The new comment.
        :param request: The current request.
        """
        from .notifications import notify_of_new_comment
        notify_of_new_comment(self, comment, request, comment.author)

    def can_edit(self, user):
        """
        Return True if the given user can edit this ticket.
        """
        return user == self.submitter or user.has_perm('bugtracker.change_issueticket')

    def render_description(self, save=False):
        """
        Render the description. Save the model only if ``save`` is True.
        """

        # Render HTML
        allow_titles_in_ticket = self.submitter.has_perm('bugtracker.allow_titles_in_ticket')
        allow_alerts_box_in_ticket = self.submitter.has_perm('bugtracker.allow_alerts_box_in_ticket')
        allow_text_colors_in_ticket = self.submitter.has_perm('bugtracker.allow_text_colors_in_ticket')
        allow_cdm_extra_in_ticket = self.submitter.has_perm('bugtracker.allow_cdm_extra_in_ticket')
        force_nofollow_in_ticket = not self.submitter.has_perm('bugtracker.allow_raw_link_in_ticket')
        content_html, content_text, _ = render_document(self.description,
                                                        allow_titles=allow_titles_in_ticket,
                                                        allow_code_blocks=True,
                                                        allow_alerts_box=allow_alerts_box_in_ticket,
                                                        allow_text_formating=True,
                                                        allow_text_extra=True,
                                                        allow_text_alignments=True,
                                                        allow_text_directions=True,
                                                        allow_text_modifiers=True,
                                                        allow_text_colors=allow_text_colors_in_ticket,
                                                        allow_spoilers=True,
                                                        allow_figures=True,
                                                        allow_lists=True,
                                                        allow_todo_lists=True,
                                                        allow_definition_lists=True,
                                                        allow_tables=True,
                                                        allow_quotes=True,
                                                        allow_footnotes=True,
                                                        allow_acronyms=True,
                                                        allow_links=True,
                                                        allow_medias=True,
                                                        allow_cdm_extra=allow_cdm_extra_in_ticket,
                                                        force_nofollow=force_nofollow_in_ticket,
                                                        render_text_version=True,
                                                        merge_footnotes_html=True,
                                                        merge_footnotes_text=True)
        self.description_html = content_html
        self.description_text = content_text

        # Save if required
        if save:
            # Avoid infinite loop by calling directly super.save
            super(IssueTicket, self).save(update_fields=('description_html', 'description_text'))


def _redo_tickets_description_rendering(sender, **kwargs):
    """
    Redo text rendering of all issue tickets.
    :param sender: Not used.
    :param kwargs: Not used.
    """
    for ticket in IssueTicket.objects.all():
        ticket.render_description(save=True)

render_engine_changed.connect(_redo_tickets_description_rendering)


class IssueComment(models.Model):
    """
    Bug issue ticket's comment model (also called "issue update" by some developers).
    An issue comment is made of:
    - a related issue, related comments of an issue are available in the IssueTicket model using ``comments``.
    - an author, submitted ticket's comments are available in the User model using ``issues_comments``.
    - a publication date,
    - and finally the comment text.
    """

    issue = models.ForeignKey(IssueTicket,
                              db_index=True,  # Database optimization
                              editable=False,
                              related_name='comments',
                              verbose_name=_('Related issue'))

    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               db_index=True,  # Database optimization
                               related_name='issues_comments',
                               verbose_name=_('Comment author'))

    pub_date = models.DateTimeField(_('Publication date'),
                                    db_index=True,  # Database optimization
                                    auto_now_add=True)

    body = RenderTextField(_('Comment text'),
                           default='',
                           blank=True)

    body_html = models.TextField(_('Comment text (raw HTML)'))

    body_text = models.TextField(_('Comment text (raw text)'))

    author_ip_address = models.GenericIPAddressField(_('Author IP address'),
                                                     default=None,
                                                     blank=True,
                                                     null=True)

    last_modification_date = models.DateTimeField(_('Last modification date'),
                                                  auto_now=True)

    class Meta:
        verbose_name = _('Issue comment')
        verbose_name_plural = _('Issue comments')
        get_latest_by = 'pub_date'
        ordering = ('pub_date',)

    def save(self, *args, **kwargs):
        """
        Save the comment.
        :param kwargs: super save() kwargs
        :param args: super save() args
        :return None
        """

        # Render body text
        self.render_body()

        # Save the comment
        super(IssueComment, self).save(*args, **kwargs)

    def __str__(self):
        return 'Comment for issue "%s": "%s..."' % (self.issue.title, self.short_body())

    def get_absolute_url(self):
        """
        Return the permalink to this issue.
        The permalink is nothing more than the parent issue permalink, with the suffix ``#comment-PK``.
        """
        nb_comments_before_this_comments = IssueComment.objects \
            .filter(issue=self.issue, id__lt=self.id) \
            .count()
        page_nb_for_this_comment = (nb_comments_before_this_comments + 1) // NB_ISSUE_COMMENTS_PER_PAGE
        page_str = '?page=%d' % page_nb_for_this_comment if page_nb_for_this_comment > 1 else ''
        return '%s%s#comment-%d' % (self.issue.get_absolute_url(), page_str, self.id)

    def get_absolute_url_simple(self):
        """
        Return the permalink to this issue. This vesion use the redirection view to avoid extra SQL query.
        """
        return reverse('bugtracker:comment_detail', kwargs={'pk': self.pk})

    def get_report_url(self):
        """
        Return the "report" permalink for this comment.
        """
        return reverse('bugtracker:comment_report', kwargs={'pk': self.pk})

    def short_body(self):
        """ Return the 20th first char of the comment body. """
        return self.body_text[:20]
    short_body.short_description = _('Comment text')

    def render_body(self, save=False):
        """
        Render the comment body. Save the model only if ``save`` is True.
        """

        # Render HTML
        allow_titles_in_comment = self.author.has_perm('bugtracker.allow_titles_in_comment')
        allow_alerts_box_in_comment = self.author.has_perm('bugtracker.allow_alerts_box_in_comment')
        allow_text_colors_in_comment = self.author.has_perm('bugtracker.allow_text_colors_in_comment')
        allow_cdm_extra_in_comment = self.author.has_perm('bugtracker.allow_cdm_extra_in_comment')
        force_nofollow_in_comment = not self.author.has_perm('bugtracker.allow_raw_link_in_comment')
        content_html, content_text, _ = render_document(self.body,
                                                        allow_titles=allow_titles_in_comment,
                                                        allow_code_blocks=True,
                                                        allow_alerts_box=allow_alerts_box_in_comment,
                                                        allow_text_formating=True,
                                                        allow_text_extra=True,
                                                        allow_text_alignments=True,
                                                        allow_text_directions=True,
                                                        allow_text_modifiers=True,
                                                        allow_text_colors=allow_text_colors_in_comment,
                                                        allow_spoilers=True,
                                                        allow_figures=True,
                                                        allow_lists=True,
                                                        allow_todo_lists=True,
                                                        allow_definition_lists=True,
                                                        allow_tables=True,
                                                        allow_quotes=True,
                                                        allow_footnotes=True,
                                                        allow_acronyms=True,
                                                        allow_links=True,
                                                        allow_medias=True,
                                                        allow_cdm_extra=allow_cdm_extra_in_comment,
                                                        force_nofollow=force_nofollow_in_comment,
                                                        render_text_version=True,
                                                        merge_footnotes_html=True,
                                                        merge_footnotes_text=True)
        self.body_html = content_html
        self.body_text = content_text

        # Save if required
        if save:
            # Avoid infinite loop by calling directly super.save
            super(IssueComment, self).save(update_fields=('body_html', 'body_text'))


def _redo_ticket_comments_body_rendering(sender, **kwargs):
    """
    Redo text rendering of all issue ticket comments.
    :param sender: Not used.
    :param kwargs: Not used.
    """
    for comment in IssueComment.objects.all():
        comment.render_body(save=True)

render_engine_changed.connect(_redo_ticket_comments_body_rendering)


class IssueChange(models.Model):
    """
    Bug issue ticket's change/history model.
    An issue change is made of:
    - a related issue, related changes of an issue are available in the IssueTicket model using ``changes``.
    - a related comment, changes are always related to a comment and available using ``IssueComment.changes``.
    - a change date,
    - a changed field,
    - the old and new value of the field.
    """

    issue = models.ForeignKey(IssueTicket,
                              db_index=True,  # Database optimization
                              editable=False,
                              related_name='changes',
                              verbose_name=_('Related issue'))

    comment = models.ForeignKey(IssueComment,
                                db_index=True,  # Database optimization
                                editable=False,
                                related_name='changes',
                                verbose_name=_('Related comment'))

    change_date = models.DateTimeField(_('Change date'),
                                       db_index=True,  # Database optimization
                                       auto_now_add=True)

    field_name = models.CharField(_('Field name'),
                                  max_length=255)

    old_value = models.TextField(_('Old value'),
                                 default='',
                                 blank=True)

    new_value = models.TextField(_('New value'),
                                 default='',
                                 blank=True)

    class Meta:
        verbose_name = _('Issue change')
        verbose_name_plural = _('Issue changes')
        get_latest_by = 'change_date'
        ordering = ('change_date',)


class IssueTicketSubscription(models.Model):
    """
    Bug issue ticket's subscription model.
    Really simple model used to store user subscription for a specific issue ticket.
    After subscribed to a ticket, if the ticket get new comment the user will be noticed.
    A bug issue ticket subscription is made of:
    - a related issue,
    - a related user,
    - an "active" flag used to avoid creating/deleting subscription entry multiple time on PEBCAK.
    """

    issue = models.ForeignKey(IssueTicket,
                              db_index=True,  # Database optimization
                              related_name='subscribers',
                              verbose_name=_('Related issue'))

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             db_index=True,  # Database optimization
                             related_name='ticket_subscriptions',
                             verbose_name=_('Subscriber'))

    active = models.BooleanField(_('Active'),
                                 default=True)

    objects = IssueTicketSubscriptionManager()

    class Meta:
        unique_together = (('issue', 'user'),)
        verbose_name = _('Issue ticket subscription')
        verbose_name_plural = _('Issue ticket subscriptions')
        ordering = ('-active',)

    def __str__(self):
        return 'Subscription of "%s" for issue #%d' % (self.user.username, self.issue.pk)


class BugTrackerUserProfile(models.Model):
    """
    Bug tracker's user profile data model.
    """

    user = AutoOneToOneField(settings.AUTH_USER_MODEL,
                             related_name='bugtracker_profile',
                             primary_key=True,
                             editable=False,
                             verbose_name=_('Related user'))

    notify_of_new_issue = models.BooleanField(_('Notify me of new issue'),
                                              default=False)

    notify_of_reply_by_default = models.BooleanField(_('Notify me of new reply by default'),
                                                     default=True)

    last_comment_date = models.DateTimeField(_('Last comment date'),
                                             default=None,
                                             blank=True,
                                             null=True)

    objects = BugTrackerUserProfileManager()

    class Meta:
        verbose_name = _('Bug tracker user profile')
        verbose_name_plural = _('Bug tracker user profiles')

    def __str__(self):
        return 'Bugtracker user\'s profile of "%s"' % self.user.username

    def is_flooding(self):
        """
        Returns ``True`` if the user has post something less than ``NB_SECONDS_BETWEEN_COMMENTS`` seconds from now.
        Returns ``False`` if the user has never post something.
        :return: bool ``True`` if the user is flooding (= trying to post two messages before the
        ``NB_SECONDS_BETWEEN_COMMENTS`` seconds delay is reached).
        """
        if self.last_comment_date is None:
            return False
        now = timezone.now()
        delta = now - self.last_comment_date
        return delta.total_seconds() < NB_SECONDS_BETWEEN_COMMENTS

    def rearm_flooding_delay_and_save(self):
        """
        Re-arm the anti flood delay and save the model.
        """
        self.last_comment_date = timezone.now()
        self.save(update_fields=('last_comment_date',))
