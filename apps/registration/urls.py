"""
Registration URLCONF for the registration app.
"""

from django.conf.urls import url

from . import views


# URL patterns configuration
urlpatterns = (

    # User registration impossible (not allowed in settings.py)
    url(r'^impossible/$', views.register_user_closed, name='registration_closed'),

    # User registration (step 1: registration)
    url(r'^$', views.register_user, {
        'post_register_redirect': 'registration:registration_done',
        'html_email_template_name': 'registration/activate_user_email.html'
    }, name='registration_register'),

    # User registration (step 2: registration done, waiting for activation)
    url(r'^ok/$', views.register_user_done, name='registration_done'),

    # User registration (step 3: account activation)
    url(r'^activation/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<activation_key>[0-9A-Za-z]+)/$',
        views.activate_user, {
            'post_activate_redirect': 'registration:registration_complete'
        }, name='registration_activate'),

    # User registration (step 4: account activated)
    url(r'^activation/ok/$', views.activate_user_complete, name='registration_complete'),
)