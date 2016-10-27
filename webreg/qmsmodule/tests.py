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


def main():
    qms = QMS(GOOD_CACHE_SETTINGS, 1)
    doctors = qms.get_all_doctors(u'СПЕЦ2')
    for doc in doctors:
        print(doc.qqc244, doc.specialization, doc.firstName, doc.lastName, doc.patronymic, doc.IsActive)


if __name__ == '__main__':
    main()
