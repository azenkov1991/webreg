from qmsintegration.models import get_external_variables
from constance import config


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
        q = get_external_variables(locals())
        qqc244n = user_profile.qmsuser.qqc244
        print (q['qqc244'])
        print (q['qqc153'])
        # Если лабораторное назначение
        # Если обычное назначение
        return fn(user_profile, patient, specialist, service, date, cell, additional_data)
    return create_appointment_in_qms







