from datetime import datetime
from main.logic import find_patient_by_polis_number
from main.models import Clinic
from django.contrib.auth.models import User
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class PolisNumberBackend(object):
    def authenticate(self, username=None, polis_number=None, birth_date=None, polis_seria=None):
        patient_writer_username = settings.PATIENT_WRITER_USER
        try:
            patient_writer_user = User.objects.get(username=patient_writer_username)
        except User.DoesNotExist:
            raise ImproperlyConfigured("Не найден пользователь для записи по умолчанию")
        if username == patient_writer_username:
            return patient_writer_user

        if not polis_number:
            return None
        patient = find_patient_by_polis_number(polis_number, birth_date, polis_seria)

        if not patient:
            return None
        if patient.user:
            return patient.user
        else:
            return patient_writer_user

    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
