"""
URLCONF for the file attachments app.
"""

from django.conf.urls import url
from django.views.generic import RedirectView
from django.core.urlresolvers import reverse_lazy

from . import views

# URL patterns configuration
urlpatterns = (

    # Forum index page
    url(r'^$', RedirectView.as_view(url=reverse_lazy('home:index'), permanent=True)),

    # Forum's Attachments view
    url(r'^(?P<pk>[0-9]+)/$', views.attachment_download, name='attachment_download'),
)
