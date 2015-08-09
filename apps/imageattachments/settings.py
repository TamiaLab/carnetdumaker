"""
Custom settings for the image attachments app.
"""

from django.conf import settings


# Number of image attachments per page
NB_IMG_ATTACHMENTS_PER_PAGE = getattr(settings, 'NB_IMG_ATTACHMENTS_PER_PAGE', 25)

# Upload directory name for all image attachments.
IMG_ATTACHMENT_UPLOAD_DIR_NAME = getattr(settings, 'IMG_ATTACHMENT_UPLOAD_DIR_NAME', 'img_attachments')

# Height in pixels of the small thumbnail of any image attachment
IMG_ATTACHMENT_SMALL_THUMBNAIL_HEIGHT = getattr(settings, 'IMG_ATTACHMENT_SMALL_THUMBNAIL_HEIGHT', 150)

# Width in pixels of the small thumbnail of any image attachment
IMG_ATTACHMENT_SMALL_THUMBNAIL_WIDTH = getattr(settings, 'IMG_ATTACHMENT_SMALL_THUMBNAIL_WIDTH', 150)

# Height in pixels of the medium thumbnail of any image attachment
IMG_ATTACHMENT_MEDIUM_THUMBNAIL_HEIGHT = getattr(settings, 'IMG_ATTACHMENT_MEDIUM_THUMBNAIL_HEIGHT', 300)

# Width in pixels of the medium thumbnail of any image attachment
IMG_ATTACHMENT_MEDIUM_THUMBNAIL_WIDTH = getattr(settings, 'IMG_ATTACHMENT_MEDIUM_THUMBNAIL_WIDTH', 300)

# Height in pixels of the large thumbnail of any image attachment
IMG_ATTACHMENT_LARGE_THUMBNAIL_HEIGHT = getattr(settings, 'IMG_ATTACHMENT_LARGE_THUMBNAIL_HEIGHT', 640)

# Width in pixels of the large thumbnail of any image attachment
IMG_ATTACHMENT_LARGE_THUMBNAIL_WIDTH = getattr(settings, 'IMG_ATTACHMENT_LARGE_THUMBNAIL_WIDTH', 640)
