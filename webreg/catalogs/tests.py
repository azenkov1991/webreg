from django.test import TestCase

# Create your tests here.
from catalogs.management.commands.loadmkb import *
from qmsintegration.models import *

qmsdb = QmsDB.objects.get(name="test")
load_mkb(1,qmsdb.settings)
