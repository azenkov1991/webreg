from django.db.models import Q
from patient_writer.models import SpecializationConfig, SpecialistConfig


def get_allowed_slot_types(user_profile, patient, department, specialization):
    years_old = patient.age
    try:
        specialization_config = SpecializationConfig.objects.get(
            specialization=specialization,
            department_config=department.departmentconfig
        )
        allowed_slot_types = (user_profile.get_allowed_slots() & specialization_config.slot_types.all()). \
            exclude(Q(slottypeconfig__min_age__gt=years_old) |
                    Q(slottypeconfig__max_age__lt=years_old)). \
            values_list('id', flat=True)
    except SpecializationConfig.DoesNotExist:
        allowed_slot_types = []
    return allowed_slot_types


def get_specialist_service(specialist):
    """
    :param specialist:
    :return:
     Возвращает услугу для специалиста
    """
    # если есть SpecialistConfig код услуги оттуда
    try:
        service = specialist.specialistconfig.service
    # иначе из настроек специализации
    except SpecialistConfig.DoesNonExist:
        service = specialist.specialization.specializationconfig.service
    return service

