from django.conf.urls import url
from patient_writer.views import PatientWriteFirstStep, PatientWriteSecondStep
urlpatterns = [
    url(r'^input_first_step/$',PatientWriteFirstStep.as_view(),name="input_first_step"),
    url(r'^input_second_step/$',PatientWriteSecondStep.as_view(),name="input_second_step")
]