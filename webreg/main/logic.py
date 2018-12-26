import datetime
import logging
from main.models import *
from qmsintegration import decorators as qms

log = logging.getLogger("webreg")


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
    # проверка на ограничение по количеству разрешенных услуг
    restriction = NumberOfServiceRestriction.get_restriction(date, user_profile, service)
    if restriction and (not (restriction.remain > 0)):
        raise AppointmentError("Превышен лимит назначения" + exception_details)
    # проверка на ограничение по типу слота
    if cell and cell.slot_type:
        slot_restrictions = user_profile.get_slot_restrictions()
        if slot_restrictions.exists():
            if not (cell.slot_type in slot_restrictions):
                raise AppointmentError("Нарушено ограничение на тип слота" + exception_details)

    # проверка допустимых услуг у сайта
    try:
        site_service_restriction = SiteServiceRestriction.objects.get(site_id=user_profile.site.id)
        allowed_services_for_site = site_service_restriction.services.all()
        if allowed_services_for_site.exists():
            if service not in allowed_services_for_site:
                raise AppointmentError("Попытка назначения услуги не разрешенной для сайта" + exception_details)
    except SiteServiceRestriction.DoesNotExist:
            pass

    # проверка доступных для назначения специалистов
    specialist_restrictions = user_profile.profile_settings.specialist_restrictions.all()
    if specialist_restrictions.exists():
        if specialist not in specialist_restrictions:
            raise AppointmentError("Специалист не разрешен для назначения" + exception_details)

    # проверка доступных для назначения услуг
    service_restrictions = user_profile.profile_settings.service_restrictions.all()
    if service_restrictions.exists():
        if service not in service_restrictions:
            raise AppointmentError("Услуга не разрешена для назначения" + exception_details)

    try:
        appointment = Appointment(user_profile=user_profile, date=date,
                                  specialist=specialist, service=service,
                                  patient=patient)
        if cell:
            appointment.cell = cell
            cell.free = False
            cell.save()
        if additional_data:
            appointment.additional_data = additional_data
        appointment.save()
        if restriction:
            restriction.increment()
        return appointment
    except Exception as ex:
        log.error(str(ex))
        raise AppointmentError("Ошибка при сохранении модели назначения" + exception_details)

Appointment.create_appointment = create_appointment


@qms.cancel_appointment
def cancel_appointment(appointment):
    try:
        cell = appointment.cell
        if cell:
            cell.free = True
            cell.save()
        appointment.safe_delete()
    except Exception as e:
        raise AppointmentError(str(e))

Appointment.cancel_appointment = cancel_appointment


@qms.get_free_cells
def get_free_cells(specialist, date_from, date_to):
    cells = Cell.objects.filter(date__range=(date_from, date_to),
                                specialist_id=specialist.id,
                                free=True)
    return cells
Cell.get_free_cells = get_free_cells


@qms.find_patient_by_polis_number
def find_patient_by_polis_number(polis_number, birth_date, polis_seria=None):
    try:
        return Patient.objects.get(
            polis_number=polis_number,
            polis_seria=polis_seria,
            birth_date=birth_date,
        )
    except Patient.DoesNotExist:
        return None


@qms.find_patient_by_birth_date
def find_patient_by_birth_date(clinic, first_name, last_name, middle_name, birth_date):
    try:
        return Patient.objects.get(first_name=first_name,
                                   last_name=last_name,
                                   middle_name=middle_name,
                                   birth_date=birth_date,
                                   clinic=clinic)
    except Patient.DoesNotExist:
        return None


@qms.create_patient
def create_patient(clinic, first_name, last_name, middle_name, birth_date, polis_nmber=None, polis_seria=None):
    patient = Patient(first_name=first_name,
                      last_name=last_name,
                      middle_name=middle_name,
                      birth_date=birth_date,
                      polis_number=polis_nmber,
                      polis_seria=polis_seria)
    patient.clinic = clinic
    patient.save()
    return patient


@qms.update_patient_phone_number
def update_patient_phone_number(patient, phone_number):
    patient.phone = phone_number
    patient.save()
