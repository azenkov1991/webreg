import unittest
from main.models import *
from catalogs.models import OKMUService


class TestMainModule(unittest.TestCase):
    def setUp(self):
        self.clinic = Clinic(name="СКЦ", city="Красноярск", address="Vbhdsfdsf")
        self.clinic.save()
        self.department = Department(name="Поликлиника1", clinic=self.clinic)
        self.department.save()
        self.service1 = OKMUService(code="A01.01.01", name="Прием терапевта", is_finished=1, level=4)
        self.service1.save()
        self.service2 = OKMUService(code="A01.01.02", name="Прием терапевта2", is_finished=1, level=4)
        self.service2.save()
        self.specialist = Specialist(fio="Терапевт Петр Иванович",
                                     specialization="Терапевт",
                                     department=self.department)
        self.specialist.save()
        self.specialist.performing_services.add(self.service1)
        self.specialist.performing_services.add(self.service2)
        date1 = datetime.date.today() + datetime.timedelta(1)
        date2 = datetime.date.today() - datetime.timedelta(2)
        self.cell1 = Cell(date=date1,
                          time_start=datetime.time(10, 0),
                          time_end=datetime.time(10, 30))
        self.cell1.specialist = self.specialist
        self.cell2 = Cell(date=date2,
                          time_start=datetime.time(10, 0),
                          time_end=datetime.time(10, 30))
        self.cell1.specialist = self.specialist
        self.cell2.specialist = self.specialist
        self.cell1.save()
        self.cell2.save()

        self.patient = Patient(first_name="Иванов", last_name="Иван", middle_name="Иванович",
                               birth_date=datetime.date(1991, 12, 3),
                               polis_number="123456789012345")
        self.patient.save()

    def test_create_legal_appointment(self):
        try:
            Appointment.create_appointment(self.patient, self.specialist, self.service1,
                                           datetime.date.today() + datetime.timedelta(1),
                                           self.cell1)
        except AppointmentError:
            assert False
    # def test_create_appintment_past(self):


