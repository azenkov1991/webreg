# -*- coding: utf-8 -*-
import datetime
from django.test import TestCase
from qmsmodule.qmsfunctions import *

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

GOOD_CACHE_SETTINGS2 = {
    'CONNECTION_PARAM': {
        'user': '_system',
        'password': 'SYS',
        'host': '10.1.1.8',
        'port': '1972',
        'wsdl_port': '57772',
        'namespace': 'SKCQMS'
    },
    'CACHE_CODING': 'cp1251',
    'DATABASE_CODE': u'СКЦ'
}


class TestQmsFunctions(TestCase):
    def setUp(self):
        self.qms = QMS(TEST_BASE_SETTINGS)

    def test_create_appointment_schedule(self):
        qqc244n = "vABdAAоABAD"
        Du = "B01.047.01"
        qqc244 = "vABdAAuAAAM"
        date = datetime.date(2016, 7, 18)
        time_start =  datetime.time(14, 30)
        time_end = datetime.time(14, 45)
        qqc153 = "vABAJnb"
        qqc1860 = self.qms.create_appointment(qqc244n, qqc153, qqc244, Du, date, time_start, time_end)
        self.assertTrue(qqc1860, "qqc1860 не должно быть пусто")
        self.qms.query.execute_query('Cancel1860', qqc1860)

    def test_create_appointment_order(self):
        qqc244n = "vABdAAоABAD"
        Du = "B01.047.01"
        qqc244 = "vABdAAuAAAM"
        date = datetime.date(2016, 7, 18)
        qqc153 = "vABAJnb"
        qqc1860 = self.qms.create_appointment(qqc244n, qqc153, qqc244, Du, date)
        self.assertTrue(qqc1860, "qqc1860 не должно быть пусто")
        self.qms.query.execute_query('Cancel1860', qqc1860)

    def test_create_lab_appointment(self):
        qqc244n = "vABdAAоABAD"
        Du = "A09.05.023"
        qqc244 = "vABdAApASAA"
        date = datetime.datetime.today()
        qqc153 = "vABAJnb"
        (qqc1860, lab_number) = self.qms.create_laboratory_appointment(qqc244n, qqc153, qqc244, Du, date)
        self.assertTrue(qqc1860, "qqc1860 не должно быть пусто")
        self.qms.query.execute_query('Cancel1860', qqc1860)

    def test_create_lab_appointment_with_lab_param(self):
        qqc244n = "vABdAAоABAD"
        Du = "A08.05.004"
        qqc244 = "vABdAApASAA"
        date = datetime.datetime.today()
        qqc153 = "vABAJnb"
        (qqc1860, lab_number) = self.qms.create_laboratory_appointment(qqc244n, qqc153, qqc244, Du, date,
                                                                       {"lab_speciman": "Кровь_цельная_венозная",
                                                                        "cl_lab_condition": "19-24",
                                                                        "contingent_code": "102"})
        self.assertTrue(qqc1860, "qqc1860 не должно быть пусто")
        self.qms.query.execute_query("GG", "1860", "pCodKO", qqc1860)
        self.assertEqual(self.qms.query.result, "102")
        self.qms.query.execute_query("GG", "1860", "qlsClinCode", qqc1860)
        self.assertEqual(self.qms.query.result, "19-24")
        self.qms.query.execute_query('Cancel1860', qqc1860)







