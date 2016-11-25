from qmsintegration.models import *
from constance import config
from main.models import AppointmentError
from qmsmodule.qmsfunctions import QMS


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

    if config.QMS_INTEGRATION_ENABLE:
        return decorator
    else:
        return false_decorator


@check_enable
def create_appointment(fn):
    def create_appointment_in_qms(user_profile, patient, specialist, service, date, cell=None, additional_data=None):
        qqc244 = get_external_id(specialist)
        qqc153 = get_external_id(patient)
        qqc244n = user_profile.qmsuser.qqc244
        clinic = user_profile.clinic
        if not clinic:
            clinic = specialist.department.clinic
        qms = QMS(clinic.qmsdb.settings)
        lab_number = None
        # Если лабораторное назначение
        if service.type == "Лаборатория":
            qqc1860, lab_number = qms.create_laboratory_appointment(qqc244n, qqc153, qqc244,
                                                                    service.code, date, additional_data)
        # Если обычное назначение
        else:
            qqc1860 = qms.create_appointment(qqc244n, qqc153, qqc244, service.code, date,
                                             cell.time_start if cell else None,
                                             cell.time_end if cell else None)
        if not qqc1860:
            raise AppointmentError("Ошибка интегации с qms")

        appointment = fn(user_profile, patient, specialist, service, date, cell, additional_data)
        set_external_id(appointment, qqc1860)
        if lab_number:
            appointment.additional_data["lab_numper"] = lab_number
            appointment.save()
        return appointment
    return create_appointment_in_qms







