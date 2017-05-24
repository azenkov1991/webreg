from registration.models import RegistrationProfile
from django.template.loader import render_to_string
from django.conf import settings


class PatientRegistrationProfile(RegistrationProfile):
    def send_activation_email(self, site):
        """
        Send an activation email to the user associated with this
        ``RegistrationProfile``.

        """
        ctx_dict = {'activation_key': self.activation_key,
                    'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
                    'user': self.user,
                    'site': site}
        subject = render_to_string('patient_writer/accounts/email/activation_email_subject.txt',
                                   ctx_dict)
        # Force subject to a single line to avoid header-injection
        # issues.
        subject = ''.join(subject.splitlines())
        message = render_to_string('patient_writer/accounts/email/activation_email.html',
                                   ctx_dict)
        self.user.email_user(subject, '', settings.DEFAULT_FROM_EMAIL, html_message=message)

    class Meta:
        proxy = True
