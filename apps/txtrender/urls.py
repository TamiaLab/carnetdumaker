"""
URLCONF for the text rendering app.
"""

from django.conf.urls import url

from . import views


# URL patterns configuration
urlpatterns = (

    # Preview rendering page
    url(r'^preview/$', views.preview_rendering, name='preview'),
)
