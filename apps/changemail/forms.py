"""
Forms for the change email app.
"""

from django import forms
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import ugettext_lazy as _
from django.core.mail import EmailMultiAlternatives
from django.contrib.sites.shortcuts import get_current_site

from .tokens import default_token_generator
from .settings import CHANGE_EMAIL_TIMEOUT_DAYS


class EmailChangeForm(forms.Form):
    """
    A form that lets a user change set their email address without entering the one.
    """

    new_email1 = forms.EmailField(label=_("New email address"),
                                  max_length=254)

    new_email2 = forms.EmailField(label=_("New email address (repeat)"),
                                  max_length=254)

    def clean_new_email2(self):
        """
        Check if the two address fields match.
        """
        email1 = self.cleaned_data.get('new_email1')
        email2 = self.cleaned_data.get('new_email2')
        if email1 and email2 and email1 != email2:
                raise forms.ValidationError(
                    _("The two email addresses didn't match."),
                    code='email_mismatch',
                )
        return email2

    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """
        Sends a django.core.mail.EmailMultiAlternatives to `to_email`.
        :param subject_template_name: The template nale to be used for the email subject.
        :param email_template_name: The template nale to be used for the email body.
        :param context: The context for the template.
        :param from_email: The sender address.
        :param to_email: The recipient address.
        :param html_email_template_name: The template nale to be used for the email HTML body.
        """

        # Craft the email subject and body content
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        # Craft the email
        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, 'text/html')

        # Send the email
        email_message.send(fail_silently=True)

    def save(self,
             request,
             subject_template_name,
             email_template_name,
             html_email_template_name=None,
             domain_override=None,
             use_https=False,
             token_generator=default_token_generator,
             from_email=None):
        """
        Generates a one-use only link for changing email address and sends to the user.
        :param domain_override: The domain name to used instead of ``request.site``. None to disable.
        :param subject_template_name: The template name to be used for the email subject.
        :param email_template_name: The template name to be used for the email body.
        :param use_https: Set to true to generate HTTPS links instead of HTTP links.
        :param token_generator: The token genertor to be used.
        :param from_email: The ``from`` email to be used.
        :param request: The current request.
        :param html_email_template_name: The template name to be used for the email HTML body.
        """
        email = self.cleaned_data['new_email1']
        user = request.user
        if not domain_override:
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain
        else:
            site_name = domain = domain_override
        context = {
            'email': email,
            'addressb64': urlsafe_base64_encode(force_bytes(email)),
            'confirmation_timeout_days': CHANGE_EMAIL_TIMEOUT_DAYS,
            'domain': domain,
            'site_name': site_name,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'user': user,
            'token': token_generator.make_token(user),
            'protocol': 'https' if use_https else 'http',
        }

        self.send_mail(subject_template_name, email_template_name,
                       context, from_email, user.email,
                       html_email_template_name=html_email_template_name)
