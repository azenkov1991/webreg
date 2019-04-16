from django.conf.urls import url, include
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.decorators.clickjacking import xframe_options_exempt
from infomat_writer.views import PatientWriteFirstStep, PatientWriteSecondStep, Confirm,\
    TalonView, logout






urlpatterns = [
    url(r'^input_first_step/(?P<department>[\d+]+)/$', xframe_options_exempt(PatientWriteFirstStep.as_view()), name="input_first_step"),
    url(r'^input_second_step/$', xframe_options_exempt(PatientWriteSecondStep.as_view()), name="input_second_step"),
    url(r'^confirm/$', xframe_options_exempt(Confirm.as_view()), name="confirm"),
    url(r'^agreement/$', xframe_options_exempt(TemplateView.as_view(template_name="infomat_writer/agreement.html")), name="agreement"),
    url(r'^talon/$', xframe_options_exempt(TalonView.as_view()), name="talon"),
    url(r'^accounts/logout/$', xframe_options_exempt(logout),
        {
            'template_name': "infomat_writer/logout.html",
        },
        name="account_logout"),
]



