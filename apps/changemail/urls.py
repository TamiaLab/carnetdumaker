"""
URLCONF for the change email app.
"""

from django.conf.urls import url

from . import views


# URL patterns configuration
urlpatterns = (

    # Step 1: request email change
    url(r'^$', views.change_email, {
        'post_change_redirect': 'myaccountmail:email_change_done',
        'email_template_name': 'changemail/email_change_email.txt',
        'html_email_template_name': 'changemail/email_change_email.html',
        'subject_template_name': 'changemail/email_change_subject.txt'
    }, name='email_change'),

    # Step 2: confirmation link sent
    url(r'^ok/$', views.change_email_done, name='email_change_done'),

    # Step 3 confirm request
    url(r'^confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<addressb64>[0-9A-Za-z_\-]+)/'
        r'(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.change_email_confirm, {
            'post_confirm_redirect': 'myaccountmail:email_change_complete'
        },
        name='email_change_confirm'),

    # Step 4: Email changed
    url(r'^fait/$', views.change_email_complete, name='email_change_complete'),
)
