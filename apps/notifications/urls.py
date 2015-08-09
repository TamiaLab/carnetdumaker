"""
URLCONF for the notification app.
"""

from django.conf.urls import url

from . import views


# URL patterns configuration
urlpatterns = (

    # Notifications index page(s)
    url(r'^$', views.notification_list, name='index'),
    url(r'^lues/$', views.notification_list, {'filterby': 'read'}, name='notification_read_list'),
    url(r'^non-lues/$', views.notification_list, {'filterby': 'unread'}, name='notification_unread_list'),

    # Mark all as read confirmation view
    url(r'^non-lues/menage/$', views.mark_all_as_read, name='mark_all_as_read'),

    # My account view
    url(r'^mon-compte/$', views.my_account_show, name='myaccount'),

    # Notification detail page
    url(r'^(?P<pk>[0-9]+)/$', views.notification_detail, name='notification_detail'),
)
