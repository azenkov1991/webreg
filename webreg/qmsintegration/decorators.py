import logging
import datetime
from constance import config
from main.models import AppointmentError, Patient, PatientError, Clinic, Service
from qmsintegration.models import *
from qmsmodule.qmsfunctions import QMS
from qmsmodule.cachequery import CacheQueryError
from .common import update_specialist_timetable

log = logging.getLogger('qmsdecorators')


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

        clinic = user_profile.clinic
        if not clinic:
            clinic = specialist.department.clinic

        try:
            qms_user = QmsUser.objects.get(
                user_profile=user_profile, qmsdb=clinic.qmsdb
            )
            qqc244n = qms_user.qqc244
        except QmsUser.DoesNotExist:
            raise AppointmentError("Не указан ресурс Qms выполняющий назначения")

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
                            service = Service.objects.get(
                                code=new_code,
                                clinic=patient.clinic_attached
                            )
                        except Service.DoesNotExist:
                            raise AppointmentError("Не найдена услуга повторного приема")
                # Проверка занятости ячейки в qms
                if cell:
                    qms.query.execute_query("CellIsFree", qqc244, date.strftime("%Y%m%d"),
                                            cell.time_start.strftime("%H:%M"),
                                            cell.time_end.strftime("%H:%M"))
                    if not qms.query.result:
                        raise AppointmentError("Ячейка уже занята")
                try:
                    episode_type = specialist.department.qmsdepartment.episode_type
                except QmsDepartment.DoesNotExist:
                    episode_type = 1

                is_create_if = clinic.qmsdb.cre293

                qqc1860 = qms.create_appointment(qqc244n, qqc153, qqc244, service.code, date,
                                                 cell.time_start if cell else None,
                                                 cell.time_end if cell else None,
                                                 episode_type,
                                                 is_create_if,
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
    def find_patient_by_birth_date_in_qms(clinic, first_name, last_name, middle_name, birth_date):
        patient = fn(clinic, first_name, last_name, middle_name, birth_date)
        if patient:
            return patient
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
                                                                    clinic=clinic,
                                                                    defaults={'polis_number':patient_data['polis_number'],
                                                                    'polis_seria': patient_data['polis_seria']})
                set_external_id(patient, patient_data['patient_qqc'], qmsdb=clinic.qmsdb)
                return patient
        except CacheQueryError:
            raise QmsIntegrationError("Ошибка интеграции с Qms")
    return find_patient_by_birth_date_in_qms


@check_enable
def find_patient_by_polis_number(fn):
    def find_patient_by_polis_number_in_qms(polis_number, birth_date, polis_seria=None):
        clinics = Clinic.objects.all()
        # информация о пациенте во всех базах qms
        patient_information_in_qms = []

        try:
            for clinic in clinics:
                qms = QMS(clinic.qmsdb.settings)
                patient_data = qms.get_patient_information(
                    polis_number=polis_number,
                    polis_seria=polis_seria,
                    birth_date=birth_date
                )
                # если пациент найден в базе и прикреплен
                if patient_data:
                    is_patient_attached, comparison_date = qms.check_patient_register(patient_data['patient_qqc'])

                    # для сортровки, если пациент не прикреплен или нет даты
                    if (not comparison_date) or (not is_patient_attached):
                        comparison_date = datetime.date(1000, 12, 31)
                    patient_information_in_qms.append((comparison_date, patient_data, clinic))

            # если пациент найден и прикреплен к нескольким базам, то это ошибка
            # но по дате сверке находим какая все таки база
            if len(patient_information_in_qms) > 1:
                log.error('Пациент прикреплен к нескольким базам. Пациент: ' + str(patient_data))

            # если пациент не найден ни в одной базе qms
            if not len(patient_information_in_qms):
                return None

            # сортировка по дате сверки прикрепления
            patient_information_in_qms.sort(key=lambda x: x[0], reverse=True)
            patient_data = patient_information_in_qms[0][1]
            clinic = patient_information_in_qms[0][2]

            # если пациент найден в базе и прикреплен
            patient, created = Patient.objects.update_or_create(
                defaults={'first_name': patient_data['first_name'],
                          'last_name': patient_data['last_name'],
                          'middle_name': patient_data['middle_name'],
                          'clinic_attached': clinic,
                          },
                polis_number=polis_number,
                birth_date=birth_date,
                polis_seria=polis_seria,

            )
            # Добавление связи со всеми поликлиниками
            patient.clinics.add(*[pi[2] for pi in patient_information_in_qms])
            set_external_id(patient, patient_data['patient_qqc'], qmsdb=clinic.qmsdb)
            return patient

        except CacheQueryError:
            raise PatientError("Ошибка при поиске пациента в Qms")
    return find_patient_by_polis_number_in_qms


@check_enable
def create_patient(fn):
    def create_patient_in_qms(clinic, first_name, last_name, middle_name,
                              birth_date, polis_number=None, polis_seria=None):
        try:
            qms = QMS(clinic.qmsdb.settings)
            qqc153 = qms.create_patient(first_name, last_name, middle_name, birth_date, polis_number, polis_seria)
            if not qqc153:
                raise QmsIntegrationError("Ошибка при создании пациента в Qms")
            patient = fn(clinic, first_name, last_name, middle_name, birth_date, polis_number, polis_seria)
            if clinic:
                set_external_id(patient, qqc153, qmsdb=clinic.qmsdb)
            else:
                set_external_id(patient, qqc153)
        except CacheQueryError:
            raise PatientError("Ошибка при создании пациента в Qms")
        return patient
    return create_patient_in_qms


@check_enable
def update_patient_phone_number(fn):
    def update_patient_phone_number_in_qms(patient, phone_number):
        fn(patient, phone_number)
        # для всех клиник пациента обновить телефон
        clinic = patient.clinic_attached
        qms = QMS(clinic.qmsdb.settings)
        qqc153 = get_external_id(patient, clinic.qmsdb)
        if clinic.qmsdb.update_phone:
            try:
                qms.query.execute_query('UpdatePatientPhoneNumber', qqc153, phone_number)
            except CacheQueryError:
                raise PatientError("Ошибка обновления телефона в Qms")
    return update_patient_phone_number_in_qms
