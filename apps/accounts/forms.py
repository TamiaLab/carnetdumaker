"""
Forms for the user accounts app.
"""

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.files.images import get_image_dimensions

from .models import UserProfile
from .settings import (AVATAR_HEIGHT_SIZE_PX,
                       AVATAR_WIDTH_SIZE_PX,
                       AVATAR_HEIGHT_SIZE_PX_MAX,
                       AVATAR_WIDTH_SIZE_PX_MAX)


class UserProfileModificationForm(forms.ModelForm):
    """
    The ``UserProfileModificationForm`` form allow user to change his first and last name,
    and his profile information. This form does not allow modification of the email
    address for security reasons. A dedicated form (with link validation and so) must be used
    for the modification of the email address.
    """

    first_name = forms.CharField(widget=forms.TextInput,
                                 max_length=30,
                                 required=False,
                                 label=_('First name'))

    last_name = forms.CharField(widget=forms.TextInput,
                                max_length=30,
                                required=False,
                                label=_('Last name'))

    class Meta:

        model = UserProfile

        fields = ('avatar',
                  'first_name',
                  'last_name',
                  'timezone',
                  'preferred_language',
                  'country',
                  'first_last_names_public',
                  'email_public',
                  'search_by_email_allowed',
                  'online_status_public',
                  'accept_newsletter',
                  'gender',
                  'location',
                  'company',
                  'biography',
                  'signature',
                  'website_name',
                  'website_url',
                  'jabber_name',
                  'skype_name',
                  'twitter_name',
                  'facebook_url',
                  'googleplus_url',
                  'youtube_url')

    def __init__(self, *args, **kwargs):
        super(UserProfileModificationForm, self).__init__(*args, **kwargs)

        # Pre-fill first name and last name from the related user model
        user = self.instance.user
        self.fields['first_name'].initial = user.first_name
        self.fields['last_name'].initial = user.last_name

    def clean_avatar(self):
        """
        Clean the newly uploaded avatar (if any).
        Check dimensions to avoid up-scaling of image or Denial-Of-Service by uploading ultra-large photo.
        """
        avatar = self.cleaned_data.get('avatar', None)
        if avatar:
            dimensions = get_image_dimensions(avatar)
            if not dimensions:
                # FIXME Dead code? ImageField seem to raise invalid_image error if dimension cannot be determined.
                raise forms.ValidationError(_('Cannot get image\'s dimensions. Please upload a valid image file.'),
                                            code='avatar_garbage')
            w, h = dimensions
            if w < AVATAR_WIDTH_SIZE_PX or h < AVATAR_HEIGHT_SIZE_PX:
                raise forms.ValidationError(_('Uploaded avatar\'s image is too small. '
                                              'Minimum dimensions are %(minh)dx%(minw)d pixels.'),
                                            params={'minh': AVATAR_HEIGHT_SIZE_PX,
                                                    'minw': AVATAR_WIDTH_SIZE_PX},
                                            code='avatar_toosmall')
            if w > AVATAR_WIDTH_SIZE_PX_MAX or h > AVATAR_HEIGHT_SIZE_PX_MAX:
                raise forms.ValidationError(_('Uploaded avatar\'s image is too big. '
                                              'Maximum dimensions are %(maxh)dx%(maxw)d pixels.'),
                                            params={'maxh': AVATAR_HEIGHT_SIZE_PX_MAX,
                                                    'maxw': AVATAR_WIDTH_SIZE_PX_MAX},
                                            code='avatar_toobig')
        return avatar

    def save(self, *args, **kwargs):
        """
        Save the form. Alter ``User`` and ``UserProfile`` at the same time.
        :param args: For super()
        :param kwargs: For super()
        :return: The saved profile instance.
        """
        res = super(UserProfileModificationForm, self).save(*args, **kwargs)

        # Save the first and last name of the associated user
        user = self.instance.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()

        # Return the saved profile instance.
        return res
