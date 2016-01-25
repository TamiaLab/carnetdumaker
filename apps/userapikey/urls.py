"""
URLCONF for the user API keys app.
"""

from django.conf.urls import url

from . import views


# URL patterns configuration
urlpatterns = (

    # Index view (show the current API key)
    url(r'^$', views.show_mykey, name='index'),

    # Regenerate key view
    url(r'^regenerer-clef/$', views.regen_mykey, name='regen_mykey'),
)
