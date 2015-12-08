"""
URLCONF for the user accounts app (part 2/2).
"""

from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views


# User accounts URL patterns configuration
urlpatterns = (

    # My account page
    url(r'^$', views.my_account_show, name='index'),

    # Password change
    url(r'^modification-mot-de-passe/$', auth_views.password_change, {
        'post_change_redirect': 'myaccount:password_change_done',
        'template_name': 'accounts/password_change_form.html'
    }, name='password_change'),

    url(r'^modification-mot-de-passe/ok/$', auth_views.password_change_done, {
        'template_name': 'accounts/password_change_done.html'
    }, name='password_change_done'),
)
