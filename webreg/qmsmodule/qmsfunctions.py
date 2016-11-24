# -*- coding: utf-8 -*-
import logging
import re
import datetime
from util.datetime import daterange

try:
    from .cachequery import *
    from .qmsqueriesnames import QMS_QUERIES
except SystemError:
    from cachequery import *
    from qmsqueriesnames import QMS_QUERIES

ODBC = 1
SOAP = 2

log = logging.getLogger("qmsfunctions")

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
                ('birth_date', 'polis_number'), True) or
                'patient_id' in kwargs):
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

    def create_appointment(self, user, patient, specialist, service, date, time_start=None, time_end=None):
        """
        Функция создания назначения в qms
        :param user: qqc244 специалиста от которого назначаем
        :param patient:  qqc153 пациента
        :param specialist: qqc244 специалиста к кторому назанчаем
        :param service: код ОКМУ услуги
        :param date: дата назначения
        :param time: время назначения. Если время назначения None, то назначение в очередь
        :return:
        возвращает qqc1860 назначения или None
        """

        # TODO: добавить во входные аргументы additional_data и брать оттуда pNDiag, pKDo, Nnapr...
        # TODO: если услуга прием найти по специализации предыдущий эпизод
        self.query.execute_query("Create174", user, patient,
                                 date.strftime("%Y%m%d"), None, None, 1, None, None)
        qqc174 = self.query.result
        if not qqc174:
            log.error("Не создан эпизод в qms. " + str(locals()))
            return None
        self.query.execute_query("Create186", user, date.strftime("%Y%m%d"),
                                 datetime.datetime.now().strftime("%H:%M"), qqc174)
        qqc186 = self.query.result
        if not qqc186:
            log.error("Не создана услуга ввода назначений. " + str(locals()))
            return None
        if time_start:
            # назначение в расписание
            self.query.execute_query("Create1860Schedule", specialist, qqc186, date.strftime("%Y%m%d"),
                                     time_start.strftime("%H:%M") + "-" + time_end.strftime("%H:%M"),
                                     service)
        else:
            # назначенеи в очередь
            self.query.execute_query("Create1860", specialist, qqc186, date.strftime("%Y%m%d"),
                                     (date + datetime.timedelta(7)).strftime("%Y%m%d"),
                                     None, service)

        (qqc1860, status) = tuple(self.query.fetch_all()[0])
        if status != "назначение создано":
            log.error(status + str(locals()))
            return None
        return qqc1860

    def create_laboratory_appointment(self, user, patient, specialist, service, date, lab_param=None):
        """
        Создание лабораторнх назначений в qms
        :param user: qqc244 Пользователя в qms
        :param patient: qqc153
        :param specialist: qqc244
        :param service: Du
        :param date: Дата назначения datetime
        :param lab_param - словарь необязательных параметров лабораторного назначения
            lab_speciman лабораторный образец
            contingent_code код контингента обследованных
            preg_week срок беременности в неделях
            cl_lab_condition	клинические условия
            height	рост пациета
            weight	вес пациента
            day_diur суточный диурез
            cmnt примечание для лаборатории
        :return:
        qqc1860 назначения
        """
        self.query.execute_query("Create174", user, patient,
                                 date.strftime("%Y%m%d"), None, None, 1, None, None)
        qqc174 = self.query.result
        if not qqc174:
            log.error("Не создан эпизод в qms. " + str(locals()))
            return None
        self.query.execute_query("Create186Lab", user, date.strftime("%Y%m%d"),
                                 datetime.datetime.now().strftime("%H:%M"), qqc174)
        qqc186 = self.query.result
        if not qqc186:
            log.error("Не создана услуга ввода назначений. " + str(locals()))
            return None
        lab_param_str = ""
        if lab_param:
            lab_param_str = lab_param.get("lab_speciman", "") + "~" + \
                                    lab_param.get("contingent_code", "") + "~" + \
                                    lab_param.get("preg_week", "") + "~" + \
                                    lab_param.get("cl_lab_condition", "") + "~" + \
                                    lab_param.get("height", "") + "~" + \
                                    lab_param.get("day_diur", "") + "~" + \
                                    lab_param.get("cmnt", "")
        self.query.execute_query("Create1860Lab", specialist, qqc186, date.strftime("%Y%m%d"),
                                 (date + datetime.timedelta(7)).strftime("%Y%m%d"),
                                 None, service, lab_param_str)
        (qqc1860, lab_number, status) = tuple(self.query.fetch_all()[0])
        if status != "назначение создано":
            log.error(status + str(locals()))
            return None
        return qqc1860, lab_number
