from django.db.models import Q
from patient_writer.models import SpecializationConfig


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

