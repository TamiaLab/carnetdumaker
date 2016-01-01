"""
Root URLCONF for the CarnetDuMaker project.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.sitemaps import views as sitemaps_views

from apps.accounts.sitemap import AccountsSitemap
from apps.announcements.sitemap import (AnnouncementsSitemap,
                                        AnnouncementTagsSitemap)
from apps.blog.sitemap import (ArticlesSitemap,
                               ArticleTagsSitemap,
                               ArticleCategoriesSitemap)
from apps.bugtracker.sitemap import IssueTicketsSitemap
from apps.forum.sitemap import (ForumsSitemap,
                                ForumThreadsSitemap)
from apps.imageattachments.sitemap import ImageAttachmentsSitemap
from apps.licenses.sitemap import LicensesSitemap
from apps.snippets.sitemap import CodeSnippetsSitemap
from apps.staticpages.sitemap import StaticPagesSitemap


# Patch admin site
admin.site.site_title = 'TamiaLab admin'
admin.site.site_header = 'TamiaLab administration'


# Root URL patterns configuration
urlpatterns = patterns('',

    # Home page
    url(r'^', include('apps.home.urls', namespace='home')),

    # Search engine
    url(r'^recherche/', include('haystack.urls', namespace='search')),

    # Blog / Forum / Boutique
    url(r'^articles/', include('apps.blog.urls', namespace='blog')),
    url(r'^forum/', include('apps.forum.urls', namespace='forum')),
    url(r'^boutique/', include('apps.shop.urls', namespace='shop')),

    # Paid membership and billing
    # TODO url(r'^abonnements/', include('apps.membership.urls', namespace='membership')),
    # TODO url(r'^factures/', include('apps.billing.urls', namespace='billing')),

    # Image attachments
    url(r'^images/', include('apps.imageattachments.urls', namespace='imageattachments')),

    # User public profiles
    url(r'^membres/', include('apps.accounts.urls', namespace='accounts')),

    # My account
    url(r'^mon-compte/', include('apps.accounts.myaccount_urls', namespace='myaccount')),
    url(r'^mon-compte/modification-adresse-email/', include('apps.changemail.urls', namespace='myaccountmail')),

    # Log watcher account history
    url(r'^mon-compte/historique-connexion/', include('apps.loginwatcher.urls', namespace='loginwatcher')),

    # User login and registration
    url(r'^authentification/', include('apps.registration.auth_urls', namespace='auth')),
    url(r'^inscription/', include('apps.registration.urls', namespace='registration')),

    # Notifications
    url(r'^notifications/', include('apps.notifications.urls', namespace='notifications')),

    # Private messages
    url(r'^messages/', include('apps.privatemsg.urls', namespace='privatemsg')),

    # Bug tracker
    url(r'^bugtracker/', include('apps.bugtracker.urls', namespace='bugtracker')),

    # Announcements
    url(r'^annonces/', include('apps.announcements.urls', namespace='announcements')),

    # code snippets
    url(r'^snippets/', include('apps.snippets.urls', namespace='snippets')),

    # User badges
    # TODO url(r'^badges/', include('apps.badges.urls', namespace='badges')),

    # Static pages
    url(r'^pages/', include('apps.staticpages.urls', namespace='staticpages')),

    # Content licenses
    url(r'^licences/', include('apps.licenses.urls', namespace='licenses')),
    url(r'^licences/', include('apps.blog.license_urls', namespace='bloglicense')),

    # Content report pages
    url(r'^signalement/', include('apps.contentreport.urls', namespace='contentreport')),

    # Text rendering preview
    url(r'^api/texte/', include('apps.txtrender.urls', namespace='txtrender')),

    # Instant Payment Notification callback hook listener(s)
    # TODO url(r'^api/ipn/', include('apps.payments.urls', namespace='payments')),

    # Admin pages
    url(r'^admin/', include(admin.site.urls)),
)

# Sitemap index and section
sitemaps = {
    'accounts': AccountsSitemap,
    'announcements': AnnouncementsSitemap,
    'announcement_tas': AnnouncementTagsSitemap,
    'blog_articles': ArticlesSitemap,
    'blog_tags': ArticleTagsSitemap,
    'blog_categories': ArticleCategoriesSitemap,
    'bugtracker': IssueTicketsSitemap,
    'forum_forums': ForumsSitemap,
    'forum_threads': ForumThreadsSitemap,
    'imageattachments': ImageAttachmentsSitemap,
    'licenses': LicensesSitemap,
    'snippets': CodeSnippetsSitemap,
    'staticpages': StaticPagesSitemap,
}
urlpatterns += patterns('',
    (r'^sitemap\.xml$', sitemaps_views.index, {'sitemaps': sitemaps}),
    (r'^sitemap-(?P<section>.+)\.xml$', sitemaps_views.sitemap, {'sitemaps': sitemaps}),
)

# Static/media files serving for debug ONLY, static() do nothing when DEBUG=False
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Debug toolbar
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )
