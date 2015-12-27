"""
Utilities for the blog app.
"""

from apps.twitter.utils import publish_link_on_twitter


def publish_article_on_twitter(article):
    """
    Publish the given article on Twitter.
    :param article: The article to be published.
    :return: The tweet ID on success, False on error.
    """
    return publish_link_on_twitter(article.title, article.get_absolute_url())
