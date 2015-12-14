"""
URLCONF for the log watcher app.
"""

from django.conf.urls import url

from . import views


# URL patterns configuration
urlpatterns = (

    # Log events index page
    url(r'^$', views.events_history, name='index'),
)
