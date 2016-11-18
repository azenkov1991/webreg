from qmsintegration.models import get_external_variables


def create_appointment(fn):
    def create_appointment_in_qms(patient, specialist, service, date, cell=None, additional_data=None):
        q = get_external_variables(locals())
        return fn(patient, specialist, service, date, cell, additional_data)
        # print (q['qqc244'])
        # print (q['qqc153'])
        # Если лабораторное назначение
        # Если обычное назначение

    return create_appointment_in_qms







