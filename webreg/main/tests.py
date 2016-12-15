import datetime
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
        self.profile_settings = ProfileSettings(name="test")
        self.profile_settings.save()
        self.site = Site(name="test", domain="127.0.0.1")
        self.site.save()
        self.user_profile = UserProfile(user=self.user,
                                        profile_settings=self.profile_settings,
                                        site=self.site)
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
        date2 = datetime.date.today() + datetime.timedelta(2)
        self.slot_type1 = SlotType(name="Тип слота1", clinic=self.clinic)
        self.slot_type1.save()
        self.slot_type2 = SlotType(name="Тип слота2", clinic=self.clinic)
        self.slot_type2.save()
        self.cell1 = Cell(date=date1,
                          time_start=datetime.time(10, 0),
                          time_end=datetime.time(10, 30),
                          slot_type=self.slot_type1)
        self.cell1.specialist = self.specialist
        self.cell2 = Cell(date=date2,
                          time_start=datetime.time(10, 0),
                          time_end=datetime.time(10, 30),
                          slot_type=self.slot_type2)
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

    def test_number_of_service_restriction(self):
        restriction = NumberOfServiceRestriction(user_profile=self.user_profile,
                                                 service=self.service1,
                                                 number=3,
                                                 date_start=datetime.date.today(),
                                                 date_end=datetime.date.today() + datetime.timedelta(5))
        restriction.save()
        ap = self.create_appointment(self.user_profile, self.patient, self.specialist, self.service1,
                                     datetime.date.today() + datetime.timedelta(1))
        ap2 = self.create_appointment(self.user_profile, self.patient, self.specialist, self.service1,
                                      datetime.date.today() + datetime.timedelta(2))
        ap3 = self.create_appointment(self.user_profile, self.patient, self.specialist, self.service1,
                                      datetime.date.today() + datetime.timedelta(3))
        restriction = NumberOfServiceRestriction.get_restriction(datetime.date.today(), self.user_profile,
                                                                 self.service1)
        self.assertEqual(restriction.remain, 0)
        with self.assertRaises(AppointmentError):
            ap4 = self.create_appointment(self.user_profile, self.patient, self.specialist, self.service1,
                                          datetime.date.today() + datetime.timedelta(4))

        ap5 = self.create_appointment(self.user_profile, self.patient, self.specialist, self.service1,
                                      datetime.date.today() + datetime.timedelta(8))

    def test_slot_type_restriction(self):

        restriction = SlotRestriction(profile_settings=self.profile_settings, slot_type=self.slot_type1)
        restriction.save()
        ap = self.create_appointment(self.user_profile, self.patient, self.specialist, self.service1,
                                     datetime.date.today() + datetime.timedelta(1),
                                     self.cell1)
        with self.assertRaises(AppointmentError):
            ap2 = self.create_appointment(self.user_profile, self.patient, self.specialist, self.service1,
                                          self.cell2.date,
                                          self.cell2)











