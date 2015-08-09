"""
URLCONF for the licenses app.
"""

from django.conf.urls import url

from . import views


# URL patterns configuration
urlpatterns = (

    # Article license index view
    url(r'^$', views.license_list, name='index'),

    # Article license view
    url(r'^(?P<slug>[-a-zA-Z0-9_]+)/$', views.license_detail, name='license_detail'),
)
