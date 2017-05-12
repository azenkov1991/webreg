from django.conf.urls import url
from django.views.generic.base import TemplateView
from patient_writer.views import PatientWriteFirstStep, PatientWriteSecondStep, Confirm,\
    SpecialistTimeTable, TalonView, TalonPdf, AppointmentListView, HelpView, AppointmentDetailView,\
    CancelAppointmentView
from patient_writer.api.api import AvailableSpecialists, AvailableSpecializaionsForDepartment

apiurlpatterns = [
    url(r'^avail_specialists/(?P<department_id>\d+)/(?P<specialization_id>\d+)', AvailableSpecialists.as_view()),
    url(r'^specializations_for_dep/(\d+)', AvailableSpecializaionsForDepartment.as_view()),
]
urlpatterns = [
    url(r'^input_first_step/', PatientWriteFirstStep.as_view(), name="input_first_step"),
    url(r'^input_second_step/$', PatientWriteSecondStep.as_view(), name="input_second_step"),
    url(r'^agreement/$', TemplateView.as_view(template_name="patient_writer/agreement.html"), name="agreement"),
    url(r'^confirm/$', Confirm.as_view(), name="confirm"),
    url(r'^timetable/specialist/(\d+)', SpecialistTimeTable.as_view()),
    url(r'^talon/$', TalonView.as_view(), name="talon"),
    url(r'^talon_pdf/(\d+)$', TalonPdf.as_view(), name="talon_pdf"),
    url(r'^appointment_list/', AppointmentListView.as_view(), name="appointment_list"),
    url(r'^help/$', HelpView.as_view(), name="help"),
    url(r'^cancel_appointment/(?P<pk>\d+)', CancelAppointmentView.as_view(), name="cancel_appointment"),
    url(r'^appointment_detail/(?P<pk>\d+)', AppointmentDetailView.as_view(), name="appointment_detail")
]
