import  logging
from django.core.management.base import BaseCommand, CommandError
from qmsmodule.qmsfunctions import *
from qmsintegration.models import *
from main.models import SlotType

logger = logging.getLogger("webreg")


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("dbname", help="Название настроек базы QMS из qmsintegration.OmsDB")

    def handle(self, *args, **options):
        dbname = options["dbname"]
        try:
            qmsdb = QmsDB.objects.get(name=dbname)
        except models.ObjectDoesNotExist:
            raise CommandError("Нет описания базы данных Qms с именем " + dbname)

        qms = QMS(qmsdb.settings)
        qms.query.execute_query('LoadTses', qmsdb.db_code)
        tses_list = qms.query.get_proxy_objects_list()
        for tses in tses_list:
            name = tses.name
            color = tses.color
            try:
                tses_obj = SlotType.objects.get(name=name, color=color)
            except SlotType.DoesNotExist:
                tses_obj = SlotType()

            tses_obj.name = name
            tses_obj.color = color
            tses_obj.clinic = qmsdb.clinic
            tses_obj.save()





