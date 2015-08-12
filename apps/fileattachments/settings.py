"""
Custom settings for the file attachments app.
"""

from django.conf import settings


# File attachments upload directory name
FILE_ATTACHMENTS_UPLOAD_DIR_NAME = getattr(settings, 'FILE_ATTACHMENTS_UPLOAD_DIR_NAME', 'file_attachments')

# File attachments max file count (default 4 files)
FILE_ATTACHMENTS_MAX_FILE_COUNT = getattr(settings, 'FILE_ATTACHMENTS_MAX_FILE_COUNT', 4)

# File attachments max file size (default 128KB)
FILE_ATTACHMENTS_MAX_FILE_SIZE = getattr(settings, 'FILE_ATTACHMENTS_MAX_FILE_SIZE', 1024 * 128)

# File attachments max total size (default 512KB)
FILE_ATTACHMENTS_MAX_TOTAL_SIZE = getattr(settings, 'FILE_ATTACHMENTS_MAX_TOTAL_SIZE', 1024 * 512)

# File attachments whitelist for direct display (no force download)
FILE_ATTACHMENTS_WHITELIST_FOR_INLINE_DISPLAY = getattr(settings, 'FILE_ATTACHMENTS_WHITELIST_FOR_INLINE_DISPLAY', (
    'application/pdf',
    'application/json',
    'application/xml',
    'audio/mpeg',
    'audio/mp3',
    'audio/x-wav',
    'audio/wav',
    'image/gif',
    'image/jpeg',
    'image/png',
    'image/tiff',
    'image/x-icon',
))

# Set to True to force login when user want to download a file
FILE_ATTACHMENTS_DOWNLOAD_REQUIRE_LOGIN = getattr(settings, 'FILE_ATTACHMENTS_DOWNLOAD_REQUIRE_LOGIN', False)
