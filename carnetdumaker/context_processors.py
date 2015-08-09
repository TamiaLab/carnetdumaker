"""
Extra context processors for the CarnetDuMaker app.
"""

from django.contrib.sites.shortcuts import get_current_site


def app_constants(request):
    """
    Constants context processor.
    :param request: the current request.
    :return: All constants for the app.
    """
    site = get_current_site(request)
    return {
        'APP': {
            'TITLE': 'Carnet du maker - L\'esprit Do It Yourself',
            'TITLE_SHORT': 'Carnet du maker',
            'AUTHOR': 'Fabien Batteix',
            'COPYRIGHT': 'TamiaLab 2015',
            'DESCRIPTION': 'L`\'esprit du Do It Yourself',
            'TWITTER_USERNAME': 'carnetdumaker',
            'GOOGLE_SITE_VERIFICATION_CODE': '',  # TODO
            'TWITTER_ACCOUNT_ID': '',  # TODO
            'FACEBOOK_URL': '',  # TODO
        },
        'SITE': {
            'NAME': site.name,
            'DOMAIN': site.domain,
            'PROTO': 'https' if request.is_secure() else 'http'
        }
    }
