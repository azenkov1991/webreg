from django.test import TestCase
from constance.test import override_config
from django.contrib.auth.models import User
from main.models import *


@override_config(QMS_INTEGRATION_ENABLE=False)
class TestMainModule(TestCase):
    def setUp(self):
        import main.logic
        self.create_appointment = main.logic.create_appointment
        self.cancel_appointment = main.logic.cancel_appointment
        try:
            self.user = User.objects.get(username="TestUser")
        except User.DoesNotExist:
            self.user = User(username="TestUser")
        self.user.save()
        self.user_profile = UserProfile(user=self.user)
        self.user_profile.save()
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

    def test_create_legal_appointment(self):
        try:
            ap = self.create_appointment(self.user_profile, self.patient, self.specialist, self.service1,
                                         datetime.date.today() + datetime.timedelta(1),
                                         self.cell1)
            self.cancel_appointment(ap)
        except AppointmentError:
            assert False

    def test_create_appointment_past(self):
        with self.assertRaises(AppointmentError):
            self.create_appointment(self.user_profile, self.patient, self.specialist, self.service1,
                                    datetime.date(2016, 5, 4),
                                    self.cell1)

    def test_create_second_appointment(self):
        with self.assertRaises(AppointmentError):
            ap = self.create_appointment(self.user_profile, self.patient, self.specialist, self.service1,
                                         datetime.date.today() + datetime.timedelta(1),
                                         self.cell1)
            ap = self.create_appointment(self.user_profile, self.patient, self.specialist, self.service1,
                                         datetime.date.today() + datetime.timedelta(1),
                                         self.cell1)

    def test_create_appointment_with_wrong_service(self):
        with self.assertRaises(AppointmentError):
            ap = self.create_appointment(self.user_profile, self.patient, self.specialist, self.service2,
                                         datetime.date.today() + datetime.timedelta(1),
                                         self.cell1)

    def test_create_appointment_without_cell(self):
        ap = self.create_appointment(self.user_profile, self.patient, self.specialist, self.service1,
                                     datetime.date.today() + datetime.timedelta(1))
        self.cancel_appointment(ap)

    def test_cancel_appointment(self):
        ap = self.create_appointment(self.user_profile, self.patient, self.specialist, self.service1,
                                     datetime.date.today() + datetime.timedelta(1),
                                     self.cell1)
        self.cancel_appointment(ap)
        self.assertTrue(ap.deleted)
        self.assertGreater(ap.deleted_time, ap.created_time)






