from main.models import *
from qmsintegration import decorators as qms


@qms.create_appointment
def create_appointment(user_profile, patient, specialist, service, date, cell=None, **additional_data):
    exception_details = "Пациент: " + patient.fio + " Специалист: " + specialist.fio + \
                        " Дата: " + str(date)
    if cell:
        exception_details += " Время: " + str(cell.time_start)
    # вызвать исключение если ячейка занята
    if cell and cell.appointment_set.exists():
        raise AppointmentError("Попытка назначения в занятую ячейку." + exception_details)
    # если назначение на дату и время меньше текущего
    if date < datetime.date.today():
        raise AppointmentError("Попытка назначения в прошлое." + exception_details)
    # если специалист не выполняет услугу
    if not specialist.performing_services.filter(code=service.code).exists():
        raise AppointmentError("Попытка назначение услуги, которую специалист не выполняет." + exception_details)
    # eсли ячейка не принадлежит специалисту
    if cell and (cell.specialist != specialist):
        raise AppointmentError("Ячейка не принадлежит специалисту." + exception_details)
    try:
        appointment = Appointment(user_profile=user_profile, date=date,
                                  specialist=specialist, service=service,
                                  patient=patient)
        if cell:
            appointment.cell = cell
        if additional_data:
            appointment.additional_data = additional_data
        appointment.save()
        return appointment
    except Exception as ex:
        log.error(str(ex))
        raise AppointmentError("Ошибка при сохранении модели назначения" + exception_details)

Appointment.create_appointment = create_appointment
