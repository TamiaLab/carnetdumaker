"""
Various constants and codes for the blog app.
"""

from django.utils.translation import ugettext_lazy as _


NOTE_TYPE_DEFAULT = 'default'
NOTE_TYPE_SUCCESS = 'success'
NOTE_TYPE_INFO = 'info'
NOTE_TYPE_WARNING = 'warning'
NOTE_TYPE_DANGER = 'danger'
NOTE_TYPE_CHOICES = (
    (NOTE_TYPE_DEFAULT, _('Default')),
    (NOTE_TYPE_SUCCESS, _('Success')),
    (NOTE_TYPE_INFO, _('Information')),
    (NOTE_TYPE_WARNING, _('Warning')),
    (NOTE_TYPE_DANGER, _('Danger')),
)


ARTICLE_STATUS_DRAFT = 'draft'
ARTICLE_STATUS_PUBLISHED = 'published'
ARTICLE_STATUS_DELETED = 'deleted'
ARTICLE_STATUS_CHOICES = (
    (ARTICLE_STATUS_DRAFT, _('Draft')),
    (ARTICLE_STATUS_PUBLISHED, _('Published')),
    (ARTICLE_STATUS_DELETED, _('Deleted'))
)
