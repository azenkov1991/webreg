from django.conf.urls import url, include
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import views as auth_views
from patient_writer.accounts.forms import PatientRegistrationForm
from patient_writer.accounts.views import PatientRegistrationView, PatientActivationView, login

urlpatterns = [
    url(r'^accounts/register/$', PatientRegistrationView.as_view(
            disallowed_url=reverse_lazy('patient_writer:registration_disallowed'),
            template_name='patient_writer/accounts/register.html',
            form_class=PatientRegistrationForm,
            success_url=reverse_lazy('patient_writer:registration_complete')
            ),
        name="registration"),
    url(r'^accounts/register/complete',
        TemplateView.as_view(template_name="patient_writer/accounts/registration_complete.html"),
        name="registration_complete"),
    url(r'^accounts/activate/(?P<activation_key>\w+)/$', PatientActivationView.as_view(
            template_name='patient_writer/accounts/activate.html',
            ),
        name='registration_activate'),
    url(r'^accounts/activate/complete/$', TemplateView.as_view(
        template_name='patient_writer/activation_complete.html'),
        name='activation_complete'),

    url(r'^accounts/login', login, {'template_name': "patient_writer/accounts/login.html",
                                    'authentication_form': AuthenticationForm,
                                    'extra_context': {'redirect_field_value': reverse_lazy('patient_writer:input_first_step'),
                                                      'redirect_field_name': 'next'}}, name="account_login"),

    url(r'^password/reset/$',
        auth_views.password_reset,
        {'post_reset_redirect': 'patient_writer:auth_password_reset_done',
         'email_template_name': 'patient_writer/accounts/email/password_reset_email.html',
         'html_email_template_name': 'patient_writer/accounts/email/password_reset_email.html',
         'subject_template_name': 'patient_writer/accounts/email/password_reset_subject.txt',
         'template_name': 'patient_writer/accounts/password_reset_form.html'},
        name='auth_password_reset'),
    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/'
        r'(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm,
        {'post_reset_redirect': 'patient_writer:auth_password_reset_complete',
         'template_name': 'patient_writer/accounts/password_reset_confirm.html'},
        name='auth_password_reset_confirm'),
    url(r'^password/reset/complete/$',
        auth_views.password_reset_complete,
        {'template_name': 'patient_writer/accounts/password_reset_complete.html'},
        name='auth_password_reset_complete'),
    url(r'^password/reset/done/$',
        auth_views.password_reset_done,
        {'template_name': 'patient_writer/accounts/password_reset_done.html'},
        name='auth_password_reset_done'),
]
