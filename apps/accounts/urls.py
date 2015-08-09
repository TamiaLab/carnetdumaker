"""
URLCONF for the user accounts app (part 1/2).
"""

from django.conf.urls import url

from apps.accounts import views


# User accounts URL patterns configuration
urlpatterns = (

    # Accounts list index page
    url(r'^$', views.accounts_list, name='index'),

    # Public user profile
    url(r'^(?P<username>[\w.@+-]+)/$', views.public_account_show, name="user_profile"),
)
