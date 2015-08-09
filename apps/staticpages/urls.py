"""
URLCONF for the static pages app.
"""

from django.conf.urls import url

from . import views


# URL patterns configuration
urlpatterns = (

    # Index page
    url(r'^$', views.index_page, name='index'),

    # All static pages
    url(r'^pourquoi-ce-site/$', views.why_this_site, name='why_this_site'),
    url(r'^qui-sommes-nous/$', views.about_us, name='about_us'),
    url(r'^nous-contacter/$', views.contact_us, name='contact_us'),
    url(r'^cookies/$', views.cookies_usage, name='cookies_usage'),
    url(r'^mentions-legales/$', views.legal_notices, name='legal_notices'),
    url(r'^faq/$', views.faq, name='faq'),
    url(r'^nos-engagements/$', views.our_commitments, name='our_commitments'),
    url(r'^plan-du-site/$', views.human_sitemap, name='human_sitemap'),
    url(r'^conditions-generales-d-utilisation/$', views.tos, name='tos'),
)
