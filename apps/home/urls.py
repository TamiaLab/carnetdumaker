"""
Home pages URLCONF for the home pages app.
"""

from django.conf.urls import url

from . import views


# URL patterns configuration
urlpatterns = (

    # Home index page
    url(r'^$', views.home_page, name='index'),
)
