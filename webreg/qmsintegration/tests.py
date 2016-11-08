import unittest
from .models import *


class Object(object):
    pass


class TestQmsIntegration(unittest.TestCase):
    def setUp(self):
        omt_spec = ObjectMatchingTable(internal_name="main.SpecialistTest",external_name='244')
        omt_spec.save()
        omt_patient = ObjectMatchingTable(internal_name="main.PatientTest", external_name='153')
        omt_patient.save()
        omt_app = ObjectMatchingTable(internal_name="main.AppointmentTest", external_name='1860')
        omt_app.save()

        imt_spec = IdMatchingTable(internal_id=34, external_id="vABABAB('[",
                                   object_matching_table_id=omt_spec.id)
        imt_spec.save()
        imt_patient = IdMatchingTable(internal_id=44, external_id="vABFAASD^",
                                      object_matching_table_id=omt_patient.id)
        imt_patient.save()
        imt_app = IdMatchingTable(internal_id=33, external_id="vAB'^DFC", object_matching_table_id=omt_app.id)
        imt_app.save()

    def test_get_external_variables(self):

        paient = Object()
        app = Object()
        specialist = Object()

        specialist._meta = Object()
        specialist._meta.label = "main.SpecialistTest"
        specialist.id = 34

        patient = Object()
        patient._meta = Object()
        patient._meta.label = "main.PatientTest"
        patient.id = 44

        app = Object()
        app._meta = Object()
        app._meta.label = "main.AppointmentTest"
        app.id = 33

        external_vars = (get_external_variables(locals()))

        self.assertEqual(external_vars['qqc244'], "vABABAB('[")
        self.assertEqual(external_vars['qqc153'], "vABFAASD^")
        self.assertEqual(external_vars['qqc1860'], "vAB'^DFC")





