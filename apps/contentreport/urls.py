"""
URLCONF for the content report app.
"""

from django.conf.urls import url
from django.views.generic import RedirectView
from django.core.urlresolvers import reverse_lazy

from . import views


# URL patterns configuration
urlpatterns = (

    # Index to the home page
    url(r'^$', RedirectView.as_view(url=reverse_lazy('home:index'), permanent=True), name='index'),

    # Report "thank" page
    url(r'^merci/$', views.report_content_done, name='content_report_done'),
)
