from constance import config
from main.models import AppointmentError
from catalogs.models import OKMUService
from qmsintegration.models import *
from qmsmodule.qmsfunctions import QMS
from qmsmodule.cachequery import CacheQueryError


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
    def create_appointment_in_qms(user_profile, patient, specialist, service, date, cell=None, **additional_data):
        qqc244 = get_external_id(specialist)
        qqc153 = get_external_id(patient)
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







