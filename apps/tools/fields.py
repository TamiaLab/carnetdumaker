"""
Custom database fields declaration.
"""

import os
from io import BytesIO
from PIL import Image, ImageOps

from django.db import models
from django.db.models.fields.related import SingleRelatedObjectDescriptor
from django.db.models.fields.files import ImageFieldFile
from django.core.files.base import ContentFile


class AutoSingleRelatedObjectDescriptor(SingleRelatedObjectDescriptor):
    """
    For internal use only.
    Wrap the constructor of ``SingleRelatedObjectDescriptor`` to auto-catch the
    ``DoesNotExist`` exception and create the related object (Just-In-Time algorithm).
    """
    def __get__(self, instance, instance_type=None):
        try:
            return super(AutoSingleRelatedObjectDescriptor, self).__get__(instance, instance_type)
        except self.RelatedObjectDoesNotExist:  # Previously: "related.model.DoesNotExist"
            obj = self.related.related_model(**{self.related.field.name: instance})
            # Previously: "self.related.model" (this variable now target the other end class type)
            obj.save()
            # Don't return obj directly, otherwise it won't be added
            # to Django's cache, and the first 2 calls to obj.relobj
            # will return 2 different in-memory objects
            return super(AutoSingleRelatedObjectDescriptor, self).__get__(instance, instance_type)


class AutoOneToOneField(models.OneToOneField):
    """
    OneToOneField creates related object on first call if it doesnt exist yet.
    Use it instead of original OneToOne field.
    example:
        class MyProfile(models.Model):
            user = AutoOneToOneField(User, primary_key=True)
            home_page = models.URLField(max_length=255, blank=True)
    """
    def contribute_to_related_class(self, cls, related):
        setattr(cls, related.get_accessor_name(), AutoSingleRelatedObjectDescriptor(related))


class AutoResizingImageFieldFile(ImageFieldFile):
    """
    Custom FieldFile with patched save() method which resize the image to a fixed size before saving it.
    """

    def save(self, name, content, save=True):
        """
        Patched save() method. Resize the image to a fixed size before saving it.
        :param name: The file's name.
        :param content: The file instance.
        :param save: Set to ``True`` to save the parent model.
        :return: super() result.
        """

        # Resize image before saving
        content = self.resize_image(name, content, self.field.width, self.field.height)

        # Save the image
        super(AutoResizingImageFieldFile, self).save(name, content, save)

    @staticmethod
    def resize_image(name, content, width, height):
        """
        Resize image into a thumbnail version of itself.
        :param content: The image data (File instance).
        :param width: The result image max width (in pixels).
        :param height: The result image max height (in pixels).
        """
        image = Image.open(content)
        if image.mode not in ('L', 'RGB'):
            image = image.convert('RGB')
        image = ImageOps.fit(image, (width, height), Image.ANTIALIAS)
        string = BytesIO()
        image.save(string, format='JPEG')
        new_name = '%s.jpg' % os.path.splitext(name)[0]
        return ContentFile(string.getvalue(), name=new_name)


class AutoResizingImageField(models.ImageField):
    """
    Extended ImageField that can resize image to a fixed size before saving it.
    """

    attr_class = AutoResizingImageFieldFile

    def __init__(self, *args, **kwargs):
        self.width = kwargs.pop('width', None)
        self.height = kwargs.pop('height', None)
        super(AutoResizingImageField, self).__init__(*args, **kwargs)


class ThumbnailImageFieldFile(ImageFieldFile):
    """
    Custom FieldFile with patched save() method which resize the image before saving it.
    """

    def save(self, name, content, save=True):
        """
        Patched save() method. Resize the image before saving it.
        :param name: The file's name.
        :param content: The file instance.
        :param save: Set to ``True`` to save the parent model.
        :return: super() result.
        """

        # Resize image before saving
        content = self.resize_image(name, content, self.field.width, self.field.height)

        # Save the image
        super(ThumbnailImageFieldFile, self).save(name, content, save)

    @staticmethod
    def resize_image(name, content, width, height):
        """
        Resize image into a thumbnail version of itself.
        :param content: The image data (File instance).
        :param width: The result image max width (in pixels).
        :param height: The result image max height (in pixels).
        """
        image = Image.open(content)
        if image.mode not in ('L', 'RGB'):
            image = image.convert('RGB')
        image.thumbnail((width, height), Image.ANTIALIAS)
        string = BytesIO()
        image.save(string, format='JPEG')
        new_name = '%s.jpg' % os.path.splitext(name)[0]
        return ContentFile(string.getvalue(), name=new_name)


class ThumbnailImageField(models.ImageField):
    """
    Extended ImageField that can resize image into thumbnail before saving it.
    Use the ``height_field`` and ``width_field`` attributes to store the final image size.
    """

    attr_class = ThumbnailImageFieldFile

    def __init__(self, *args, **kwargs):
        self.width = kwargs.pop('width', None)
        self.height = kwargs.pop('height', None)
        super(ThumbnailImageField, self).__init__(*args, **kwargs)
