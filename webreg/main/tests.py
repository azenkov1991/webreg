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
        self.user_profile = UserProfile(profile_settings=self.profile_settings,
                                        site=self.site)
        self.user_profile.save()
        self.user_profile.user.add(self.user)
        self.clinic = Clinic(name="СКЦ", city="Красноярск", address="Vbhdsfdsf")
        self.clinic.save()
        self.department = Department(name="Поликлиника1", clinic=self.clinic)
        self.department.save()
        self.service1 = OKMUService(code="A01.01.01", name="Прием терапевта", is_finished=1, level=4)
        self.service1.save()
        self.service2 = OKMUService(code="A01.01.02", name="Прием терапевта2", is_finished=1, level=4)
        self.service2.save()
        self.service_not_allowed_for_site = OKMUService(code="A01.05.01", name="Прием невролога",
                                                        is_finished=1, level=4)
        self.service_not_allowed_for_site.save()
        site_service_restriction = SiteServiceRestriction(site=self.site)
        site_service_restriction.save()
        site_service_restriction.services.add(self.service1, self.service2)

        self.specialist = Specialist(fio="Терапевт Петр Иванович",
                                     specialization=Specialization.objects.create(name="Терапевт"),
                                     department=self.department)
        self.specialist.save()
        self.specialist.performing_services.add(self.service1)
        self.specialist.performing_services.add(self.service_not_allowed_for_site)
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

    def test_site_services_permissions(self):
        with self.assertRaises(AppointmentError):
            ap = self.create_appointment(self.user_profile, self.patient, self.specialist,
                                     self.service_not_allowed_for_site,
                                     datetime.date.today() + datetime.timedelta(1),
                                     self.cell1)

    def test_get_allowed_services(self):
        yesterday = datetime.date.today()-datetime.timedelta(1)
        tomorrow = datetime.date.today() + datetime.timedelta(1)

        # 10 тестовых услуг
        for i in range(3,14):
            service = OKMUService(code=("A01.01." + str(i)),
                                  name="Тестовая услуга №" + str(i))
            service.save()
            #  11  12 13 не разрешены для назначения
            if i not in [11,12,13]:
                ServiceRestriction(profile_settings=self.profile_settings,
                                   service=service).save()

            # десятая услуга полностью использована
            if i==10:
                NumberOfServiceRestriction(
                    user_profile_id=self.user_profile.id,
                    service_id=service.id,
                    number=4,
                    number_of_used=4,
                    date_start=yesterday,
                    date_end=tomorrow
                ).save()

            # 8,9 услуга запрещена для сайта
            if i not in [8,9]:
                site_service_restrictions, created = SiteServiceRestriction.objects.get_or_create(
                    site_id=self.user_profile.site.id
                )
                site_service_restrictions.services.add(service)

            if i==7:
                NumberOfServiceRestriction(
                    user_profile_id=self.user_profile.id,
                    service_id=service.id,
                    number=4,
                    number_of_used=3,
                    date_start=yesterday,
                    date_end=tomorrow
                ).save()

        # в итоге услуги 3-7 должны быть доступны для назначения
        # из queryset услуг извлечение только последних цифр
        lst = list(map(lambda x: int(x.split('.')[2]),
                       self.user_profile.get_allowed_services().values_list('code',flat=True)))
        self.assertEqual(lst, list(range(3,8)), "Определение доступных услуг1")

        # с initial_query_set
        initial_query_set = OKMUService.objects.filter(code__contains="A01.01").exclude(code__in=["A01.01.3",
                                                                                                  "A01.01.4",
                                                                                                  "A01.01.5"])
        lst = list(map(lambda x: int(x.split('.')[2]),
                       self.user_profile.get_allowed_services(initial_query_set).values_list('code', flat=True)))
        self.assertEqual(lst, list(range(6, 8)),"Определение доступных услуг2")

        #без ограничений на сайт
        SiteServiceRestriction.objects.all().delete()
        lst = list(map(lambda x: int(x.split('.')[2]),
                       self.user_profile.get_allowed_services().values_list('code', flat=True)))
        self.assertEqual(lst, list(range(3, 10)),"Определение доступных услуг3")

    def test_allowed_specialists(self):
        specialization, created = Specialization.objects.get_or_create(name="Терапевт")

        for i in range(1,11):
            specialist = Specialist(fio="Специалист №" + str(i),
                                    specialization=specialization,
                                    department=self.department)
            specialist.save()
            # каждый второй специалист разрешен для назначения
            if i%2:
                SpecialistRestriction(profile_settings=self.profile_settings,
                                      specialist_id=specialist.id).save()

        # список номеров специалистов доступных для назначения
        lst = list(map(lambda x: int(x.split('№')[1]),
                       self.user_profile.get_allowed_specialists().values_list('fio',flat=True)))

        self.assertEqual(lst,[i for i in range(1,11,2)], "Определение доступных для назначений специалистов")























