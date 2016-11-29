# -*- coding: utf-8 -*-
import re
import datetime
from util.datetime import  daterange

try:
    from .cachequery import *
    from .qmsqueriesnames import QMS_QUERIES
except SystemError:
    from cachequery import *
    from qmsqueriesnames import QMS_QUERIES

ODBC = 1
SOAP = 2


class QMS:
    def __init__(self, cache_settings, connection_mode=ODBC):
        if connection_mode == ODBC:
            self.query = CacheODBCQuery(cache_settings['CONNECTION_PARAM'],
                                        QMS_QUERIES,
                                        cache_settings['CACHE_CODING'])
        elif connection_mode == SOAP:
            self.query = CacheSOAPQuery(cache_settings['CONNECTION_PARAM'],
                                        QMS_QUERIES,
                                        cache_settings['CACHE_CODING'])
        else:
            self.query = CacheODBCQuery(cache_settings['CONNECTION_PARAM'],
                                        QMS_QUERIES,
                                        cache_settings['CACHE_CODING'])
        self.DATABASE_CODE = cache_settings['DATABASE_CODE']

    def get_patient_information(self, **kwargs):
        """
        Именованые параметры:
            birth_date в формате ГГГГММДД
            first_name
            last_name
            middle_name
            polis_number
            polis_seria
        Возвращает словарь или None если пациента не найдено
        """
        # проверка аргументов ФИО + Дата рождения либо номер полиса + дата рождения
        # либо ид пациента

        if not (reduce(lambda res, element: res and element in kwargs,
                ('birth_date', 'first_name', 'last_name', 'middle_name'), True) or
                reduce(lambda res, element: res and element in kwargs,
                ('birth_date', 'polis_number'), True) or
                'patient_id' in kwargs):
            raise ValueError('Wrong arguments')
        result = {}
        if 'patient_id' in kwargs:
            self.query.execute_query('PatientDetail', kwargs['patient_id'])
            query_result = self.query.fetch_all()[0]
            if query_result[0] == "" or query_result[0] is None:
                return None
            columns = self.query.get_columns()
            query_result = dict(zip(columns, query_result))
            for (k1, k2) in zip(['first_name', 'last_name', 'middle_name', 'birth_date', 'address_reg', 'address_liv'],
                                ['pF', 'pG', 'pH', 'birthDate', 'AddressReg', 'AddressLiv']):
                result[k1] = query_result[k2]

        else:
            self.query.execute_query('SearchPatient', self.DATABASE_CODE, str(1), kwargs.get('polis_seria', ""),
                                     kwargs.get('polis_number', ""), kwargs.get('birth_date', ""),
                                     kwargs.get('first_name', ""), kwargs.get('last_name', ""),
                                     kwargs.get('middle_name', ""))
            query_result = self.query.fetch_all()[0]
            if query_result[0] != u'OK':
                return None
            print(query_result[1])
            columns = self.query.get_columns()
            query_result = dict(zip(columns, query_result))
            for (k1, k2) in zip(['birth_date', 'address_reg', 'address_liv'],
                                ['BirthDate', 'AddressReg', 'AddressLiv']):
                result[k1] = query_result[k2]
            fio = query_result['fio'].split("_")
            result['first_name'] = fio[0]
            result['last_name'] = fio[1]
            result['middle_name'] = fio[2]
        polisstr = query_result['polis']
        result['polis_number'] = re.findall(u"№ (\d*)", polisstr)[0]
        result['polis_seria'] = re.findall(u"Серия (\d*)", polisstr)[0]

        return result

    def get_patient_id(self, **kwargs):
        """
        Именованые параметры:
            birth_date в формате ГГГГММДД
            first_name
            last_name
            middle_name
            polis_number
            polis_seria
        Возвращает словарь или None если пациент не найдено
        """
        # проверка аргументов ФИО + Дата рождения либо номер полиса + дата рождения
        # либо ид пациента

        if not (reduce(lambda res, element: res and element in kwargs,
                ('birth_date', 'first_name', 'last_name', 'middle_name'), True) or
                reduce(lambda res, element: res and element in kwargs,
                ('birth_date', 'polis_number'), True)):
            raise ValueError('Wrong arguments')
        self.query.execute_query('SearchPatient', self.DATABASE_CODE, 0, kwargs.get('polis_seria', ""),
                                 kwargs.get('polis_number', ""), kwargs.get('birth_date', ""),
                                 kwargs.get('first_name', ""), kwargs.get('last_name', ""),
                                 kwargs.get('middle_name', ""))
        result = self.query.fetch_all()[0]
        if result[0] != u'OK':
                return None
        return result[3]

    def avail_spec(self, specialist_code):
        self.query.execute_query('AvailSpec', self.DATABASE_CODE, specialist_code)
        return self.query.get_proxy_objects_list()

    def get_all_doctors(self, department_code=None):
        self.query.execute_query("GetAllDoctors", self.DATABASE_CODE, department_code)
        return self.query.get_proxy_objects_list()

    def get_usl_for_spec(self, spec_qqc244):
        self.query.execute_query("SpecialistPerformingServices", spec_qqc244)
        return self.query.get_proxy_objects_list()

    def get_timetable(self, specialist, date_from, date_to):
        """

        :param specialist: qqc244 специалиста
        :param date_from: Дата начала datetime
        :param date_to: Дата конца datetime
        :return:
        Возвращает список ячееек
        Поля: date, time_start, time_end, cabinet, slot_type, okmu_list
        """
        cell_list = []
        for date in daterange(date_from, date_to):
            self.query.execute_query("RaspFreeDetail", specialist, date.strftime("%Y%m%d"), None, None, None, 1)
            for cell_item in self.query.get_proxy_objects_list():
                cell = ProxyObject()
                cell.date = date
                try:
                    time_start = cell_item.str.split("-")[0]
                    cell.time_start = datetime.time(int(time_start.split(":")[0]),
                                                    int(time_start.split(":")[1]))
                except:
                    cell.time_start = datetime.time(0, 0)
                try:
                    time_end = cell_item.str.split("-")[1]
                    cell.time_end = datetime.time(int(time_end.split(":")[0]),
                                                  int(time_end.split(":")[1]))
                except:
                    cell.time_end = datetime.time(0, 0)
                cell.slot_type = cell_item.fin
                cell.cabinet = cell_item.cabinet
                cell.okmu_list = str(cell_item.Du).split(" ")
                cell.free = cell_item.status
                cell_list.append(cell)
        return cell_list

    def create_appointment(self, patient, specialist, service, date, time=None):
        pass

    def create_laboratory_appointment(self, patient, specialit, sevice, date):
        pass
