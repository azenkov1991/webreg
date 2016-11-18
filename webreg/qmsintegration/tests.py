import unittest
from qmsintegration.models import *
from main.models import *


class Object(object):
    pass


class TestQmsIntegration(unittest.TestCase):
    def setUp(self):
        omt_spec = ObjectMatchingTable(internal_name="main.SpecialistTest",external_name='244')
        omt_spec.save()
        omt_patient = ObjectMatchingTable(internal_name="main.PatientTest", external_name='153')
        omt_patient.save()
        omt_app = ObjectMatchingTable(internal_name="main.AppointmentTest", external_name='1860')
        omt_app.save()

        imt_spec = IdMatchingTable(internal_id=34, external_id="vABABAB('[",
                                   object_matching_table_id=omt_spec.id)
        imt_spec.save()
        imt_patient = IdMatchingTable(internal_id=44, external_id="vABFAASD^",
                                      object_matching_table_id=omt_patient.id)
        imt_patient.save()
        imt_app = IdMatchingTable(internal_id=33, external_id="vAB'^DFC", object_matching_table_id=omt_app.id)
        imt_app.save()

    def test_get_external_variables(self):

        paient = Object()
        app = Object()
        specialist = Object()

        specialist._meta = Object()
        specialist._meta.label = "main.SpecialistTest"
        specialist.id = 34

        patient = Object()
        patient._meta = Object()
        patient._meta.label = "main.PatientTest"
        patient.id = 44

        app = Object()
        app._meta = Object()
        app._meta.label = "main.AppointmentTest"
        app.id = 33

        external_vars = (get_external_variables(locals()))

        self.assertEqual(external_vars['qqc244'], "vABABAB('[")
        self.assertEqual(external_vars['qqc153'], "vABFAASD^")
        self.assertEqual(external_vars['qqc1860'], "vAB'^DFC")


class TestQmsIntegrationAppointment(unittest.TestCase):
    def setUp(self):
        self.clinic = Clinic(name="СКЦ", city="Красноярск", address="Vbhdsfdsf")
        self.clinic.save()
        self.department = Department(name="Поликлиника1", clinic=self.clinic)
        self.department.save()
        self.service1 = OKMUService(code="A01.01.01", name="Прием терапевта", is_finished=1, level=4)
        self.service1.save()
        self.service2 = OKMUService(code="A01.01.02", name="Прием терапевта2", is_finished=1, level=4)
        self.service2.save()
        self.specialist = Specialist(fio="Терапевт Петр Иванович",
                                     specialization=Specialization.objects.create(name="Терапевт"),
                                     department=self.department)
        self.specialist.save()
        set_external_id(self.specialist, "244", "vABAcddssdfe")
        self.specialist.performing_services.add(self.service1)

        date1 = datetime.date.today() + datetime.timedelta(1)
        date2 = datetime.date.today() - datetime.timedelta(2)
        self.cell1 = Cell(date=date1,
                          time_start=datetime.time(10, 0),
                          time_end=datetime.time(10, 30))
        self.cell1.specialist = self.specialist
        self.cell2 = Cell(date=date2,
                          time_start=datetime.time(10, 0),
                          time_end=datetime.time(10, 30))
        self.cell1.specialist = self.specialist
        self.cell2.specialist = self.specialist
        self.cell1.save()
        self.cell2.save()

        self.patient = Patient(first_name="Иванов", last_name="Иван", middle_name="Иванович",
                               birth_date=datetime.date(1991, 12, 3),
                               polis_number="123456789012345")
        self.patient.save()
        set_external_id(self.patient, "153", "vAB1245")

    def test_create_legal_appointment(self):
        try:
            ap = Appointment.create_appointment(self.patient, self.specialist, self.service1,
                                                datetime.date.today() + datetime.timedelta(1),
                                                self.cell1)
        except AppointmentError:
            assert False



