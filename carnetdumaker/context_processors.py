"""
Extra context processors for the CarnetDuMaker app.
"""

from django.contrib.sites.shortcuts import get_current_site
from django.utils.translation import ugettext_lazy as _


def app_constants(request):
    """
    Constants context processor.
    :param request: the current request.
    :return: All constants for the app.
    """
    site = get_current_site(request)
    return {
        'APP': {
            'TITLE': _('Carnet du maker - L\'esprit Do It Yourself'),
            'TITLE_SHORT': _('Carnet du maker'),
            'AUTHOR': 'Fabien Batteix',
            'COPYRIGHT': _('TamiaLab 2015'),
            'DESCRIPTION': _('L\'esprit du Do It Yourself'),
            'TWITTER_USERNAME': 'carnetdumaker',
            'GOOGLE_SITE_VERIFICATION_CODE': '',  # TODO
            'TWITTER_ACCOUNT_ID': '3043075520',
            'FACEBOOK_URL': '',  # TODO
        },
        'SITE': {
            'NAME': site.name,
            'DOMAIN': site.domain,
            'PROTO': 'https' if request.is_secure() else 'http',
            'CURRENT_URL': request.get_full_path(),
        }
    }
