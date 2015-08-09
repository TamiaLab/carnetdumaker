"""
URLCONF for the private messages app.
"""

from django.conf.urls import url

from . import views


# URL patterns configuration
urlpatterns = (

    # Private messages inbox pages
    url(r'^$', views.msg_inbox, name='inbox'),
    url(r'^lus/$', views.msg_inbox, {'filterby': 'read'}, name='inbox_read'),
    url(r'^non-lus/$', views.msg_inbox, {'filterby': 'unread'}, name='inbox_unread'),

    # Mark all received private messages as read
    url(r'^non-lus/menage/$', views.mark_all_as_read, name='inbox_mark_all_as_read'),

    # Private messages outbox page
    url(r'^envoyes/$', views.msg_outbox, name='outbox'),

    # Private messages trash page
    url(r'^corbeille/$', views.msg_trashbox, name='trash'),

    # Permanently delete all message in the trash
    url(r'^corbeille/menage/$', views.delete_all_deleted_msg_permanently, name='delete_all_deleted_msg_permanently'),

    # Private messages compose view
    url(r'^nouveau/$', views.msg_compose, name='compose'),
    url(r'^nouveau/(?P<recipient>[\w.@+-]+)/$', views.msg_compose, name='compose_to'),

    # My account view
    url(r'^mon-compte/$', views.my_account_show, name='myaccount'),

    # blocked users views
    url(r'^mon-compte/utilisateurs-bloques/$', views.blocked_user_list, name='blocked_users'),
    url(r'^mon-compte/utilisateurs-bloques/(?P<username>[\w.@+-]+)/bloque/$', views.block_user, name='block_user'),
    url(r'^mon-compte/utilisateurs-bloques/(?P<username>[\w.@+-]+)/debloque/$', views.unblock_user, name='unblock_user'),

    # Private messages detail page
    url(r'^(?P<pk>[0-9]+)/$', views.msg_detail, name='msg_detail'),

    # Private messages reply page
    url(r'^(?P<parent_pk>[0-9]+)/repondre/$', views.msg_reply, name='msg_reply'),

    # Private messages delete / un-delete pages
    url(r'^(?P<pk>[0-9]+)/supprimer/$', views.msg_delete, name='msg_delete'),
    url(r'^(?P<pk>[0-9]+)/supprimer/definitivement/$', views.msg_delete_permanent, name='msg_delete_permanent'),
    url(r'^(?P<pk>[0-9]+)/restaurer/$', views.msg_undelete, name='msg_undelete'),
)
