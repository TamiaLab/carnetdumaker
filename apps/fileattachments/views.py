"""
Views for the file attachments app.
"""

from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.contrib.auth.views import redirect_to_login
from django.http import StreamingHttpResponse
from django.core.servers.basehttp import FileWrapper

from .settings import (FILE_ATTACHMENTS_WHITELIST_FOR_INLINE_DISPLAY,
                       FILE_ATTACHMENTS_DOWNLOAD_REQUIRE_LOGIN)
from .models import FileAttachment


def attachment_download(request, pk):
    """
    Allow user to download the given attachment.
    :param request: The current request.
    :param pk: The desired attachment pk.
    :return: StreamingHttpResponse
    """

    # Get the attachment object
    attachment_obj = get_object_or_404(FileAttachment, pk=pk)

    # Check access rights
    if not attachment_obj.parent_post.has_access(request.user):
        raise PermissionDenied()

    # Check authentication
    if FILE_ATTACHMENTS_DOWNLOAD_REQUIRE_LOGIN and not request.user.is_authenticated():
        return redirect_to_login(attachment_obj.get_absolute_url())

    # Stream the file content securely
    mimetype = attachment_obj.content_type
    response = StreamingHttpResponse(FileWrapper(attachment_obj.file.open()), content_type=mimetype)
    response['Content-Length'] = attachment_obj.size
    if mimetype not in FILE_ATTACHMENTS_WHITELIST_FOR_INLINE_DISPLAY:
        response['Content-Disposition'] = "attachment; filename=%s" % attachment_obj.filename
        response['X-Content-Type-Options'] = 'nosniff'

    # TODO Use serve() if DEBUG=True and http://wiki.nginx.org/X-accel#X-Accel-Redirect on production
    # Maybe add support by settings for https://tn123.org/mod_xsendfile/ (Apache version of X-Accel-Redirect)

    return response
