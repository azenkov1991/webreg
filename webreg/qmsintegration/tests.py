from django.test import TestCase
from django.contrib.auth.models import User
from main.logic import *
from qmsintegration.models import *
from qmsmodule.qmsfunctions import QMS

TEST_BASE_SETTINGS = {
    'CONNECTION_PARAM': {
        'user': '_system',
        'password': 'SYS',
        'host': '172.16.1.10',
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
        self.date_qms_str = self.qms.query.execute_query('SetFakeRaspOnSunday', "vABdAAuAAAC", "09:00-09:30")

        specialist_matching = ObjectMatchingTable(id=1, internal_name="main.Specialist", external_name="244")
        patient_matching = ObjectMatchingTable(id=2, internal_name="main.Patient", external_name="153")
        appointment_matching = ObjectMatchingTable(id=3, internal_name="main.Appointment", external_name="1860")
        specialist_matching.save()
        patient_matching.save()
        appointment_matching.save()

        self.user = User(username="TestUser2")
        self.user.save()
        self.user_profile = UserProfile(user=self.user)
        self.user_profile.save()
        self.qms_user = QmsUser(name="Платежка", qqc244="vABdABЪABAA", user_profile=self.user_profile)
        self.qms_user.save()
        self.clinic = Clinic(name="СКЦ", city="Красноярск", address="Vbhdsfdsf")
        self.clinic.save()
        self.qmsdb = QmsDB(name="test", clinic=self.clinic,
                           connection_param=TEST_BASE_SETTINGS['CONNECTION_PARAM'],
                           db_code="СКЦ", coding="cp1251")
        self.department = Department(name="Поликлиника1", clinic=self.clinic)
        self.department.save()
        self.service1 = OKMUService(code="B01.047.01", name="Прием врача-терапевта первичный", is_finished=1, level=4)
        self.service1.save()
        self.service2 = OKMUService(code="B01.047.02", name="Прием врача-терапевта повторный", is_finished=1, level=4)
        self.service2.save()
        self.specialist = Specialist(fio="Садилова Надежда Дмитриевна",
                                     specialization=Specialization.objects.create(name="Терапевт"),
                                     department=self.department)
        self.specialist.save()
        set_external_id(self.specialist, "vABdAAuAAAC")
        self.specialist.performing_services.add(self.service1)

        first_sunday = datetime.date.today() + datetime.timedelta(6 - datetime.date.today().weekday())
        date1 = first_sunday
        date2 = datetime.date.today() - datetime.timedelta(2)
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

        self.patient = Patient(first_name="Тест", last_name="Дарья", middle_name="Женщина",
                               birth_date=datetime.date(1991, 12, 3),
                               polis_number="123456789012345")
        self.patient.save()
        set_external_id(self.patient, "vABAJnb")

    def tearDown(self):
        self.date_qms_str = self.qms.query.execute_query('DeleteFakeRasp', "vABdAAuAAAC", self.date_qms_str)

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



