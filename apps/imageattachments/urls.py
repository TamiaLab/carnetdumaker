"""
URLCONF for the image attachments app.
"""

from django.conf.urls import url

from . import views


# URL patterns configuration
urlpatterns = (

    # Image attachments list view
    url(r'^$', views.image_attachment_list, name='index'),

    # Image attachment detail view
    url(r'^(?P<slug>[-a-zA-Z0-9_]+)/$', views.image_attachment_detail, name='image_attachment_detail'),
)
