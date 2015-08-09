"""
File storage class snippet.
"""

from django.core.files.storage import FileSystemStorage


class OverwriteStorage(FileSystemStorage):
    """
    Simple file storage class who overwrite any existing file.
    Pretty useful with mutable user-supplied file like avatar image.
    """

    def _save(self, name, content):
        """
        Save the given content to the file, overwrite any existing file if exist.
        """

        # If the filename already exists, remove it before saving
        if self.exists(name):
            self.delete(name)

        return super(OverwriteStorage, self)._save(name, content)
    
    def get_available_name(self, name, max_length=None):
        """
        Returns a filename that's free on the target storage system, and
        available for new content to be written to.
        """
        return name
