from constance import config
from main.models import AppointmentError, Patient
from catalogs.models import OKMUService
from qmsintegration.models import *
from qmsmodule.qmsfunctions import QMS
from qmsmodule.cachequery import CacheQueryError
from .common import update_specialist_timetable


def check_enable(decorator):
    """
    Декоратор для декораторов
    Проверяет есть ли натройка qms_integration_enable
    Если есть применяет декоратор
    Если нет - не применяет декоратор
    :param decorator: декоратор
    :return:
    Возвращает либо сам декоратор, если применяется настройка
    Либо декоратор который возвращает просто переданную функцию
    """

    def false_decorator(fn):
        return fn
    try:
        if config.QMS_INTEGRATION_ENABLE:
            return decorator
        else:
            return false_decorator
    except:
        return  false_decorator


@check_enable
def create_appointment(fn):
    def create_appointment_in_qms(user_profile, patient, specialist, service, date, cell=None, **additional_data):
        try:
            qqc244 = get_external_id(specialist)
            qqc153 = get_external_id(patient)
        except QmsIntegrationError:
            raise AppointmentError("Ошибка интеграции с qms")
        qqc244n = user_profile.qmsuser.qqc244
        clinic = user_profile.clinic
        if not clinic:
            clinic = specialist.department.clinic
        try:
            qms = QMS(clinic.qmsdb.settings)
            lab_number = None
            # Если лабораторное назначение
            if service.type == "Лаборатория":
                qqc1860, lab_number = qms.create_laboratory_appointment(qqc244n, qqc153, qqc244,
                                                                        service.code, date, **additional_data)
            # Если обычное назначение
            else:
                # подмена услуги с первичного приема на повторный
                if not ("повторный" in service.name):
                    qms.query.execute_query("GetSecondService", qqc153, qqc244, service.code, 30,
                                            date.strftime("%Y%m%d"))
                    new_code = qms.query.result
                    if new_code:
                        try:
                            service = OKMUService.objects.get(code=new_code)
                        except OKMUService.DoesNotExist:
                            raise AppointmentError("Не найдена услуга повторного приема")
                # Проверка занятости ячейки в qms
                if cell:
                    qms.query.execute_query("CellIsFree", qqc244, date.strftime("%Y%m%d"),
                                            cell.time_start.strftime("%H:%M"),
                                            cell.time_end.strftime("%H:%M"))
                    if not qms.query.result:
                        raise AppointmentError("Ячейка уже занята")

                qqc1860 = qms.create_appointment(qqc244n, qqc153, qqc244, service.code, date,
                                                 cell.time_start if cell else None,
                                                 cell.time_end if cell else None,
                                                 **additional_data)
            if not qqc1860:
                raise AppointmentError("Ошибка интегации с qms")
        except CacheQueryError:
            raise AppointmentError("Ошибка интеграции с qms")
        try:
            appointment = fn(user_profile, patient, specialist, service, date, cell, **additional_data)
            set_external_id(appointment, qqc1860)
            if lab_number:
                appointment.additional_data = {"lab_number": lab_number}
                appointment.save()
        except AppointmentError as ap:
            qms.query.execute_query("Cancel1860", qqc1860)
            raise ap
        return appointment
    return create_appointment_in_qms


@check_enable
def cancel_appointment(fn):
    def cancel_appointment_in_qms(appointment):
        try:
            qqc1860 = get_external_id(appointment)
        except QmsIntegrationError:
            raise AppointmentError("Ошибка интеграции с Qms")
        clinic = appointment.user_profile.clinic
        if not clinic:
            clinic = appointment.specialist.department.clinic
        try:
            qms = QMS(clinic.qmsdb.settings)
            qms.query.execute_query("Cancel1860", qqc1860)
        except CacheQueryError:
            raise AppointmentError("Ошибка интеграции с Qms")
        fn(appointment)
    return cancel_appointment_in_qms


@check_enable
def get_free_cells(fn):
    def get_free_cells_in_qms(specialist, date_from, date_to):
        clinic = specialist.department.clinic
        qms = QMS(clinic.qmsdb.settings)
        update_specialist_timetable(specialist, date_from, date_to, qms)
        return fn(specialist, date_from, date_to)
    return get_free_cells_in_qms

@check_enable
def find_patient_by_birth_date(fn):
    def find_patient_by_birth_date_in_qms(clinic, first_name,last_name, middle_name, birth_date):
        try:
            qms = QMS(clinic.qmsdb.settings)
            patient_data = qms.get_patient_information(first_name=first_name,
                                                       last_name=last_name,
                                                       middle_name=middle_name,
                                                       birth_date=birth_date)
            if patient_data:
                patient, created = Patient.objects.update_or_create(first_name=first_name,
                                                                    last_name=last_name,
                                                                    middle_name=middle_name,
                                                                    birth_date=birth_date,
                                                                    defaults={'polis_number':patient_data['polis_number'],
                                                                    'polis_seria': patient_data['polis_seria']})
                set_external_id(patient, patient_data['patient_qqc'])
                patient.clinic.add(clinic)
                return patient
        except CacheQueryError:
            raise QmsIntegrationError("Ошибка интеграции с Qms")
    return find_patient_by_birth_date_in_qms

@check_enable
def find_patient_by_polis_number(fn):
    def find_patient_by_polis_number_in_qms(clinic, polis_number, birth_date, polis_seria=None):
        try:
            qms = QMS(clinic.qmsdb.settings)
            patient_data = qms.get_patient_information(polis_number=polis_number,
                                                       polis_seria=polis_seria,
                                                       birth_date=birth_date)
            if patient_data:
                patient, created = Patient.objects.update_or_create(defaults={'first_name':patient_data['first_name'],
                                                                              'last_name':patient_data['last_name'],
                                                                              'middle_name':patient_data['middle_name']},
                                                                    polis_number=polis_number,
                                                                    birth_date=birth_date,
                                                                    polis_seria=polis_seria)
                patient.clinic.add(clinic)
                set_external_id(patient, patient_data['patient_qqc'])
                return patient
        except CacheQueryError:
            raise QmsIntegrationError("Ошибка при поиске пациента в Qms")
    return find_patient_by_polis_number_in_qms

@check_enable
def create_patient(fn):
    def create_patient_in_qms(clinic, first_name, last_name, middle_name,
                              birth_date, polis_number=None, polis_seria=None):
        try:
            qms = QMS(clinic.qmsdb.settings)
            qqc153 = qms.create_patient(first_name,last_name,middle_name, birth_date, polis_number, polis_seria)
            if not qqc153:
                raise QmsIntegrationError("Ошибка при создании пациента в Qms")
            patient = fn(clinic, first_name, last_name, middle_name, birth_date, polis_number, polis_seria)
            set_external_id(patient, qqc153)
        except CacheQueryError:
            raise QmsIntegrationError("Ошибка при создании пациента в Qms")
        return patient
    return create_patient_in_qms
