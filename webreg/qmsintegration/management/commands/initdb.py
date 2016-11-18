from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from main.models import Clinic, Department
from qmsintegration.models import QmsDB

class Command(BaseCommand):
    def handle(self, *args, **options):
        User.objects.create_superuser(username='admin', password='admin', email='')
        clinic = Clinic(name='СКЦ', city='Красноярск', address='ул. Коломенская')
        clinic.save()
        QmsDB(name='QMS', db_code='СКЦ', coding='cp1251', clinic=clinic, connection_param=
                    {"user": "_system",
                     "password": "SYS",
                     "host": "172.16.1.10",
                     "port": "1972",
                     "wsdl_port": "57772",
                     "namespace": "SKCQMS"}).save()
        Department(name='ПОЛ1', clinic=clinic).save()
        Department(name='ПОЛ2', clinic=clinic).save()
        Department(name='ПОЛ3', clinic=clinic).save()
