from django.conf.urls import url, include
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from infomat_writer.views import PatientWriteFirstStep, PatientWriteSecondStep, Confirm,\
    TalonView, logout





urlpatterns = [
    url(r'^input_first_step/', PatientWriteFirstStep.as_view(), name="input_first_step"),
    url(r'^input_second_step/$', PatientWriteSecondStep.as_view(), name="input_second_step"),
    url(r'^confirm/$', Confirm.as_view(), name="confirm"),
    url(r'^agreement/$', TemplateView.as_view(template_name="infomat_writer/agreement.html"), name="agreement"),
    url(r'^talon/$', TalonView.as_view(), name="talon"),
    url(r'^accounts/logout/$', logout,
        {
            'template_name': "infomat_writer/logout.html",
        },
        name="account_logout"),
]



