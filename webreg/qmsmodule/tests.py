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


def parse_options():
    parser = OptionParser()
    parser.add_option("--folder", dest="folder", action="store", help="foldername", default=False)
    parser.add_option("--filename", dest="filename", action="store", help="filename", default=False)
    return parser.parse_args()


def main():
    options, args = parse_options()
    assert options.folder and options.filename
    logger = set_logger_settings(options.folder, options.filename)
    qms = QMS(GOOD_CACHE_SETTINGS, logger, 1)
    doctors = qms.get_all_doctors(u'СПЕЦ2')
    for doc in doctors:
        print(doc.qqc244, doc.specialization, doc.firstName, doc.lastName, doc.patronymic, doc.IsActive)


if __name__ == '__main__':
    main()
