"""
Various functions for various things.
"""

from django.utils.text import slugify


def unique_slug(model_cls, self_obj, org_slug, org_slug_field_name, slug_source, extra_filter_kwargs=None):
    """
    Make sure the given object's slug is unique. If not, add incrementing number to the end of the slug until unique.
    :param model_cls: The model class for the object.
    :param self_obj: The current object (in database or memory, used to ignore the current slug of the object if any).
    :param org_slug: The original slug text.
    :param org_slug_field_name: The slug field name.
    :param slug_source: The source slug text (will be slugified if org_slug is not set to get an usable slug).
    :param extra_filter_kwargs: Extra keyword arguments for the filter call.
    :return: The final slug, unique right now (warning: running race possible).
    """

    # Create the slug if not already exist
    if not org_slug:
        org_slug = slugify(slug_source)

    # Craft the filter kwargs dict
    filter_kwargs = {}
    if extra_filter_kwargs is not None:
        filter_kwargs.update(extra_filter_kwargs)

    # Loop until a free slug is found
    new_slug = org_slug
    new_slug_counter = 2
    filter_kwargs[org_slug_field_name] = new_slug
    while model_cls.objects.exclude(pk=self_obj.pk).filter(**filter_kwargs).exists():
        # NOTE .exclude(pk=self.pk) resolve to .exclude(pk=None) = no effect, on object creation
        # This allow modification of slug without disabling the duplicate-slug-avoidance security.
        new_slug = '%s-%d' % (org_slug, new_slug_counter)
        new_slug_counter += 1
        filter_kwargs[org_slug_field_name] = new_slug

    return new_slug
