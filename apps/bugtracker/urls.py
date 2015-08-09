"""
URLCONF for the bug tracker app.
"""

from django.conf.urls import url
from django.views.generic import RedirectView
from django.core.urlresolvers import reverse_lazy

from apps.contentreport.views import report_content

from . import views, feeds
from .models import IssueComment
from .forms import IssueCommentReportCreationForm


# Bug tracker URL patterns configuration
urlpatterns = (

    # Index to the tickets list page
    url(r'^$', views.index, name='index'),
    url(r'^commentaires/$', RedirectView.as_view(url=reverse_lazy('bugtracker:index'), permanent=True)),

    # Issue tickets list view
    url(r'^tickets/$', views.tickets_list, name='issues_list'),

    # Issue ticket create view
    url(r'^tickets/nouveau/$', views.ticket_create, name='issue_create'),

    # Latest issue tickets feeds
    url(r'^tickets/flux/$', feeds.LatestTicketsFeed(), name='latest_issues_rss'),
    url(r'^tickets/flux/atom/$', feeds.LatestTicketsAtomFeed(), name='latest_issues_atom'),

    # Latest issue's comments feeds
    url(r'^tickets/flux-commentaires/$', feeds.LatestTicketCommentsFeed(), name='latest_issue_comments_rss'),
    url(r'^tickets/flux-commentaires/atom/$', feeds.LatestTicketCommentsAtomFeed(), name='latest_issue_comments_atom'),

    # Issue ticket detail view (and comment view)
    url(r'^tickets/(?P<pk>\d+)/$', views.ticket_show, name='issue_detail'),

    # Issue ticket update view
    url(r'^tickets/(?P<pk>\d+)/modifier/$', views.ticket_edit, name='issue_edit'),

    # Issue ticket subscription management
    url(r'^tickets/(?P<pk>\d+)/abonner/$', views.ticket_subscribe, name='issue_subscribe'),
    url(r'^tickets/(?P<pk>\d+)/desabonner/$', views.ticket_unsubscribe, name='issue_unsubscribe'),

    # Latest issue's comments feeds for a given issue
    url(r'^tickets/(?P<pk>\d+)/flux/$', feeds.LatestTicketCommentsForIssueFeed(),
        name='latest_issue_comments_for_issue_rss'),
    url(r'^tickets/(?P<pk>\d+)/flux/atom/$', feeds.LatestTicketCommentsForIssueAtomFeed(),
        name='latest_issue_comments_for_issue_atom'),

    # Shortcut for comment permalink
    url(r'^commentaires/(?P<pk>\d+)/$', views.comment_show, name='comment_detail'),
    
    # Issue ticket comment report submit view
    url(r'^commentaires/(?P<pk>\d+)/signaler/$', report_content, kwargs={
        'objects_loader': IssueComment.objects.select_related('issue', 'author'),
        'content_object_name': 'comment',
        'template_name': 'bugtracker/issueticket_report_comment.html',
        'content_report_form': IssueCommentReportCreationForm,
    }, name='comment_report'),

    # My account view
    url(r'^mon-compte/$', views.my_account_show, name='myaccount'),

    # My tickets list view
    url(r'^mon-compte/mes-tickets/$', views.my_tickets_list, name='mytickets_list'),

    # My ticket's subscriptions list view
    url(r'^mon-compte/mes-abonnements/$', views.my_ticket_subscription_list, name='myticketsubscribtions_list'),
)
