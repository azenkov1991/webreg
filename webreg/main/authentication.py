from datetime import datetime
from main.logic import find_patient_by_polis_number
from main.models import Clinic
from django.contrib.auth.models import User
from django.conf import settings

class PolisNumberBackend(object):
    def authenticate(self, username=None, password=None):
        if username==settings.PATIENT_WRITER_USER:
            user = User.objects.get(name=username)
            return user
        else:
            return None
