# -*- coding: utf-8 -*-
import unittest
from optparse import OptionParser
try:
    from .qmsfunctions import *
except SystemError:
    from qmsfunctions import *

# Create your tests here.


GOOD_CACHE_SETTINGS = {
            'CONNECTION_PARAM': {
                   'user': '_system',
                   'password': 'SYS',
                   'host': '10.1.2.105',
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


def print_doctors():
    qms = QMS(GOOD_CACHE_SETTINGS2, 1)
    doctors = qms.get_all_doctors(u'СПЕЦ2')
    for doc in doctors:
        print(doc.qqc244, doc.specialization, doc.firstName, doc.lastName, doc.middleName, doc.IsActive)


def print_okmu():
    qms = QMS(GOOD_CACHE_SETTINGS, 1)
    query = qms.query
    for level in range(1, 4):
        query.execute_query('LoadMKB', level)
        for service_fields_list in query.results():
            code = service_fields_list[0]
            name = service_fields_list[1]
            parent = service_fields_list[2]
            print (code, name, parent)


def print_timetable():
    qms = QMS(GOOD_CACHE_SETTINGS2)
    cell_list = qms.get_timetable(u'vABdAAwAEAO', datetime.date(2016, 11, 5), datetime.date(2016, 11, 15))
    for cell in cell_list:
        print(cell)


def main():
    # print_doctors()
    # print_okmu()
    print_timetable()

if __name__ == '__main__':
    main()

