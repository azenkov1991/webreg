from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from main.logic import *
from qmsintegration.models import *
from qmsmodule.qmsfunctions import QMS

TEST_BASE_SETTINGS = {
    'CONNECTION_PARAM': {
        'user': '_system',
        'password': 'SYS',
        'host': '172.16.1.12',
        'port': '1972',
        'wsdl_port': '57772',
        'namespace': 'SKCQMS'
    },
    'CACHE_CODING': 'cp1251',
    'DATABASE_CODE': u'СКЦ'
}


class Object(object):
    pass


class TestQmsIntegration(TestCase):
    def setUp(self):

        omt_spec = ObjectMatchingTable(internal_name="main.Specialist", external_name='244')
        omt_spec.save()
        omt_patient = ObjectMatchingTable(internal_name="main.Patient", external_name='153')
        omt_patient.save()
        omt_app = ObjectMatchingTable(internal_name="main.Appointment", external_name='1860')
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
        specialist._meta.label = "main.Specialist"
        specialist.id = 34

        patient = Object()
        patient._meta = Object()
        patient._meta.label = "main.Patient"
        patient.id = 44

        app = Object()
        app._meta = Object()
        app._meta.label = "main.Appointment"
        app.id = 33

        external_vars = (get_external_variables(locals()))

        self.assertEqual(external_vars['qqc244'], "vABABAB('[")
        self.assertEqual(external_vars['qqc153'], "vABFAASD^")
        self.assertEqual(external_vars['qqc1860'], "vAB'^DFC")


class TestQmsIntegrationAppointment(TestCase):
    def setUp(self):
        self.qms = QMS(TEST_BASE_SETTINGS)

        specialist_matching = ObjectMatchingTable(id=1, internal_name="main.Specialist", external_name="244")
        patient_matching = ObjectMatchingTable(id=2, internal_name="main.Patient", external_name="153")
        appointment_matching = ObjectMatchingTable(id=3, internal_name="main.Appointment", external_name="1860")
        specialist_matching.save()
        patient_matching.save()
        appointment_matching.save()

        self.user = User(username="TestUser2")
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
        qmsdb_arguments = dict(TEST_BASE_SETTINGS['CONNECTION_PARAM'])
        qmsdb_arguments.update({
            'name': "test",
            'clinic': self.clinic,
            'db_code': "СКЦ",
            'coding': "cp1251",
        })
        self.qmsdb = QmsDB(**qmsdb_arguments)
        self.qmsdb.save()
        self.qms_user = QmsUser(
            name="Платежка", qqc244="vABdABЪABAA",
            user_profile=self.user_profile,
            qmsdb=self.qmsdb
        )
        self.qms_user.save()
        self.department = Department(name="Поликлиника1", clinic=self.clinic)
        self.department.save()
        self.service1 = Service(
            code="B01.047.01", clinic=self.clinic,
            name="Прием врача-терапевта первичный", is_finished=1, level=4
        )
        self.service1.save()
        self.service2 = Service(
            code="B01.047.02", clinic=self.clinic,
            name="Прием врача-терапевта повторный", is_finished=1, level=4
        )
        self.service2.save()
        self.lab_service = Service(
            code="A08.05.004", clinic=self.clinic,
            name="Исследование уровня лейкоцитов в крови",
            type="Лаборатория", is_finished=1, level=4
        )
        self.lab_service.save()
        self.lab_service2 = Service(
            code="A09.05.023", clinic=self.clinic,
            name="Исследование_уровня_глюкозы_в_крови",
            type="Лаборатория", is_finished=1, level=4
        )
        self.lab_service2.save()

        site_permissions = SiteServiceRestriction(site=self.site)
        site_permissions.save()
        site_permissions.services.add(self.service1, self.service2, self.lab_service, self.lab_service2)
        self.specialist = Specialist(fio="Садилова Надежда Дмитриевна",
                                     specialization=Specialization.objects.create(name="Терапевт"),
                                     department=self.department)
        self.specialist.save()

        set_external_id(self.specialist, "vABdAAuAAAC")
        self.procedure_cabinet = Specialist(fio="Процедурный кабинет для внешних ЛПУ",
                                            specialization=Specialization.objects.create(name="процедурный кабиет"),
                                            department=self.department)
        self.procedure_cabinet.save()
        self.procedure_cabinet.performing_services.add(self.lab_service)
        self.procedure_cabinet.performing_services.add(self.lab_service2)
        set_external_id(self.procedure_cabinet, "vABdAApASAA")

        self.specialist.performing_services.add(self.service1)
        self.specialist.performing_services.add(self.service2)
        first_sunday = datetime.date.today() + datetime.timedelta(6 - datetime.date.today().weekday())
        date1 = first_sunday
        date2 = date1 + datetime.timedelta(7)
        self.date_qms_str = self.qms.query.execute_query('SetFakeRaspOnSunday', "vABdAAuAAAC", "09:00-09:30")
        self.date_qms_str2 = self.qms.query.execute_query('SetFakeRaspOnSunday', "vABdAAuAAAC", "10:00-10:30",
                                                          date2.strftime("%Y%m%d"))
        self.cell1 = Cell(date=date1,
                          time_start=datetime.time(9, 0),
                          time_end=datetime.time(9, 30))

        self.cell1.specialist = self.specialist
        self.cell2 = Cell(date=date2,
                          time_start=datetime.time(10, 0),
                          time_end=datetime.time(10, 30))
        self.cell1.specialist = self.specialist
        self.cell2.specialist = self.specialist
        self.cell1.save()
        self.cell2.save()

        self.patient = Patient(
            first_name="Тест", last_name="Дарья", middle_name="Женщина",
            birth_date=datetime.date(1991, 12, 3),
            polis_number="123456789012345",
            clinic_attached=self.clinic
        )
        self.patient.save()
        self.patient.clinics.add(self.clinic)

        set_external_id(self.patient, "vABAJnb", self.clinic.qmsdb)
        self.patient2 = Patient(
            first_name="Тест", last_name="Тест", middle_name="Мужчина",
            birth_date=datetime.date(1991, 12, 4),
            polis_number="123456789012345",
            clinic_attached=self.clinic
        )
        self.patient2.save()
        self.patient2.clinics.add(self.clinic)

        set_external_id(self.patient2, "vABAF.x", self.clinic.qmsdb)

    def tearDown(self):
        self.qms.query.execute_query('DeleteFakeRasp', "vABdAAuAAAC", self.date_qms_str)
        self.qms.query.execute_query('DeleteFakeRasp', "vABdAAuAAAC", self.date_qms_str2)

    def test_create_legal_appointment(self):
        try:
            ap = Appointment.create_appointment(self.user_profile, self.patient, self.specialist, self.service1,
                                                self.cell1.date,
                                                self.cell1)
            # проверка создания назначения в qms
            qqc1860 = get_external_id(ap)
            self.qms.query.execute_query("GG", "1860", "u", qqc1860)
            service_name = self.qms.query.result
            self.assertEqual(service_name, "Прием_(осмотр,_консультация)_врача-терапевта_первичный",
                             "Неверное имя создания услуги в Qms")
            self.qms.query.execute_query("GG", "1860", "pPN", qqc1860)
            service_time = self.qms.query.result
            self.assertEqual(service_time, "09:00-09:30", "Неверное время создания услуги в qms")
            self.qms.query.execute_query('Cancel1860', qqc1860)
        except AppointmentError:
            assert False

    def test_create_two_appointments_in_one_cell(self):
        with self.assertRaises(AppointmentError) as cm:
            ap = Appointment.create_appointment(self.user_profile, self.patient, self.specialist, self.service1,
                                                self.cell1.date,
                                                self.cell1)

            ap2 = Appointment.create_appointment(self.user_profile, self.patient2, self.specialist, self.service1,
                                                 self.cell1.date,
                                                 self.cell1)
        qqc1860 = get_external_id(ap)
        self.qms.query.execute_query('Cancel1860', qqc1860)
        self.assertEqual(str(cm.exception), "Ячейка уже занята")
        self.qms.query.execute_query('HardDelete174', qqc1860[0:10])

    def test_create_appointment_order(self):
        ap = Appointment.create_appointment(self.user_profile, self.patient, self.specialist, self.service1,
                                            self.cell1.date)
        qqc1860 = get_external_id(ap)
        self.qms.query.execute_query("GG", "1860", "u", qqc1860)
        service_name = self.qms.query.result
        self.assertEqual(service_name, "Прием_(осмотр,_консультация)_врача-терапевта_первичный",
                         "Неверное имя создания услуги в Qms")
        self.qms.query.execute_query("GG", "1860", "datAF", qqc1860)
        service_date = self.qms.query.result
        self.assertEqual(service_date, "0", "Неверная дата назначения в qms")
        self.qms.query.execute_query('Cancel1860', qqc1860)
        self.qms.query.execute_query('HardDelete174', qqc1860[0:10])

    def test_create_appointment_laboratory(self):
        ap = Appointment.create_appointment(self.user_profile, self.patient, self.procedure_cabinet,
                                            self.lab_service, self.cell1.date,
                                            **{"cl_lab_condition": "19-24",
                                               "contingent_code": "102",
                                               "diagnos_code": "A00.1",
                                               "diagnos_description": "He must die!!!"}
                                            )
        ap2 = Appointment.create_appointment(self.user_profile, self.patient, self.procedure_cabinet,
                                             self.lab_service2, self.cell2.date)

        qqc1860 = get_external_id(ap)
        qqc1860_2 = get_external_id(ap2)
        self.qms.query.execute_query("GG", "1860", "u", qqc1860)
        service_name = self.qms.query.result
        self.assertEqual(service_name, "Исследование_уровня_лейкоцитов_в_крови", "Неверное имя услуги в qms")
        self.qms.query.execute_query("GG", "1860", "qlsClinCode", qqc1860)
        cl_lab_condition = self.qms.query.result
        self.assertEqual(cl_lab_condition, "19-24")
        self.qms.query.execute_query("GG", "1860", "pCodKO", qqc1860)
        contingent_code = self.qms.query.result
        self.assertEqual(contingent_code, "102")
        self.assertEqual(ap.additional_data['lab_number'][0:7], "TMP" + self.cell1.date.strftime("%Y"))
        # self.assertEqual(qqc1860[0:19], qqc1860_2[0:19])
        self.qms.query.execute_query('Cancel1860', qqc1860)
        self.qms.query.execute_query('Cancel1860', qqc1860_2)
        self.qms.query.execute_query('HardDelete174', qqc1860[0:10])

    # def test_second_appointment(self):
    #     ap = Appointment.create_appointment(self.user_profile, self.patient, self.specialist, self.service1,
    #                                         self.cell1.date,
    #                                         self.cell1)
    #     ap2 = Appointment.create_appointment(self.user_profile, self.patient, self.specialist, self.service1,
    #                                          self.cell2.date,
    #                                          self.cell2)
    #     qqc1860 = get_external_id(ap)
    #     qqc1860_2 = get_external_id(ap2)
    #     self.qms.query.execute_query("GG", "1860", "u", qqc1860)
    #     service_name = self.qms.query.result
    #     self.assertEqual(service_name, "Прием_(осмотр,_консультация)_врача-терапевта_первичный")
    #     self.qms.query.execute_query("GG", "1860", "u", qqc1860_2)
    #     service_name2 = self.qms.query.result
    #     self.assertEqual(service_name2, "Прием_(осмотр,_консультация)_врача-терапевта_повторный")
    #     self.assertEqual(qqc1860[0:19], qqc1860_2[0:19], "Услуги ввода назначений должны совпадать")
    #     self.qms.query.execute_query('Cancel1860', qqc1860_2)
    #     self.qms.query.execute_query('Cancel1860', qqc1860)
    #     self.qms.query.execute_query('HardDelete174', qqc1860[0:10])

    def test_cancel_appointment(self):
        ap = Appointment.create_appointment(self.user_profile, self.patient, self.specialist, self.service1,
                                            self.cell1.date,
                                            self.cell1)
        qqc1860 = get_external_id(ap)
        self.qms.query.execute_query("GG", "1860", "u", qqc1860)
        service_name = self.qms.query.result
        self.assertEqual(service_name, "Прием_(осмотр,_консультация)_врача-терапевта_первичный",
                         "Неверное имя создания услуги в Qms")
        Appointment.cancel_appointment(ap)
        self.qms.query.execute_query("GG", "1860", "u", qqc1860)
        service_name = self.qms.query.result
        self.assertEqual(service_name, None)






