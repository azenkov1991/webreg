from django.core.management.base import BaseCommand, CommandError
from qmsintegration.models import ObjectMatchingTable


class Command(BaseCommand):
    def handle(self, *args, **options):
        specialist_matching = ObjectMatchingTable(id=1, internal_name="main.Specialist", external_name="244")
        patient_matching = ObjectMatchingTable(id=2, internal_name="main.Patient", external_name="153")
        appointment_matching = ObjectMatchingTable(id=3, internal_name="main.Appointment", external_name="1860")
        specialist_matching.save()
        patient_matching.save()
        appointment_matching.save()

