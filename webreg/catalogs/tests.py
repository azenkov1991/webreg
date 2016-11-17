from django.test import TestCase

# Create your tests here.
from catalogs.management.commands.loadmkb import *
from qmsintegration.models import *

qmsdb = QmsDB.objects.get(name="QMS")
cmd = Command()
cmd.load_mkb(qmsdb.settings)
