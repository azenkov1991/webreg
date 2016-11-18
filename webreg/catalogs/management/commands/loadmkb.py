from catalogs.models import *
from django.core.management.base import BaseCommand, CommandError
from qmsmodule.qmsfunctions import *
from qmsintegration.models import *

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("dbname", help="Название настроек базы QMS из qmsintegration.OmsDB")
        parser.add_argument("-d", "--delete", help="Перед загрузкой все диагнозы будут удалены",
                            action="store_true", dest="delete")

    def handle(self, *args, **options):
        dbname = options["dbname"]
        try:
            qmsdb = QmsDB.objects.get(name=dbname)
        except models.ObjectDoesNotExist:
            raise CommandError("Нет описания базы данных Qms с именем " + dbname)
        if options["delete"]:
            MKBDiagnos.objects.all().delete()
        self.load_mkb(cache_settings=qmsdb.settings)

    def load_mkb(self, cache_settings):
        """
        Загрузка справочников МКБ из qms
        """
        query = QMS(cache_settings).query
        for level in range(1, 5):
            query.execute_query('LoadMKB', level)
            for service_fields_list in query.results():
                code = service_fields_list[0]
                name = service_fields_list[1]
                par = service_fields_list[2]
                try:
                    parent = MKBDiagnos.objects.get(code=par)
                except MKBDiagnos.DoesNotExist:
                    parent = None
                is_finished = (level >= 4)
                if code and name:
                    try:
                        mkb_obj = MKBDiagnos.objects.get(code=code)
                    except MKBDiagnos.DoesNotExist:
                        mkb_obj = MKBDiagnos(code=code, name=name, is_finished=is_finished, level=level, parent=parent)
                    else:
                        mkb_obj.is_finished = is_finished
                        mkb_obj.level = level
                        mkb_obj.name = name
                        mkb_obj.parent = parent
                    mkb_obj.save()
