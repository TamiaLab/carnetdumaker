"""
Management command to generate a Twitter access token manually.
"""

import tweepy

from django.core.management.base import NoArgsCommand


class Command(NoArgsCommand):
    """
    This management command allow user to generate a Twitter access token manually.
    """

    help = "Generate a Twitter access token manually"

    def handle_noargs(self, **options):
        """
        Command handler.
        :param options: Not used.
        :return: None.
        """
        print('You are about to request a new token from Twitter.')
        print('Enter your consumer token and secret (from your Twitter app) below.')

        # Get consumer token and secret from stdin
        consumer_token = input('Consumer token:')
        consumer_secret = input('Consumer secret:')

        # Get the authorization URL
        print('Requesting a token from Twitter, please wait ...')
        auth = tweepy.OAuthHandler(consumer_token, consumer_secret)
        try:
            authorization_url = auth.get_authorization_url()
            print('Token acquired, please visit the following URL and write down the PIN code.')
            print('Authorization URL:', authorization_url)
        except tweepy.TweepError:
            print('Authorization Error! Failed to get request token.')
            return

        # Get the verification code
        print('Please enter the PIN code displayed on the page above.')
        verification_code = input('Verification code:')

        # Get the access token
        print('Requesting account access, please wait ...')
        try:
            access_token, access_token_secret = auth.get_access_token(verification_code)
        except tweepy.TweepError:
            print('Authorization Error! Failed to get access token.')
            return
        print('Authorization granted! ')

        # Print the access token and secret
        print('Your freshly generated access token is below.')
        print('OAuth access token:', access_token)
        print('OAuth access secret:', access_token_secret)
