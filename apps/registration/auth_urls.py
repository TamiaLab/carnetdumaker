"""
Authentication URLCONF for login, logout and password reset.
"""

from django.conf.urls import url
from django.contrib.auth import views
from django.views.generic import RedirectView
from django.core.urlresolvers import reverse_lazy


# Authentication URL patterns configuration
# See https://docs.djangoproject.com/en/1.7/topics/auth/default/#module-django.contrib.auth.views
urlpatterns = (

    # Redirect index to the connection page
    url(r'^$', RedirectView.as_view(url=reverse_lazy('auth:login'), permanent=True), name='index'),

    # Login and logout
    url(r'^connexion/$', views.login, name='login'),
    url(r'^deconnexion/$', views.logout, name='logout'),

    # Password reset link request
    url(r'^motdepasseperdu/$', views.password_reset, {
        'post_reset_redirect': 'auth:password_reset_done',
        'email_template_name': 'registration/password_reset_email.txt',
        'html_email_template_name': 'registration/password_reset_email.html'
    }, name='password_reset'),
    url(r'^motdepasseperdu/ok/$', views.password_reset_done, name='password_reset_done'),

    # Password reset (after receiving the reset link)
    url(r'^motdepasseperdu/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.password_reset_confirm, {
            'post_reset_redirect': 'auth:password_reset_complete'
        }, name='password_reset_confirm'),
    url(r'^motdepasseperdu/reset/ok/$', views.password_reset_complete, name='password_reset_complete'),
)
