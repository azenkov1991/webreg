from json import loads as jsonload
from django.core.management.base import BaseCommand, CommandError
from catalogs.models import *
from qmsmodule.qmsfunctions import *
from qmsintegration.models import *


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("dbname", help="Название настроек базы QMS из qmsintegration.OmsDB")
        parser.add_argument("-d", "--delete", help="Перед загрузкой все услуги будут удалены",
                            action="store_true", dest="delete")

    def handle(self, *args, **options):
        dbname = options["dbname"]
        try:
            qmsdb = QmsDB.objects.get(name=dbname)
        except models.ObjectDoesNotExist:
            raise CommandError("Нет описания базы данных Qms с именем " + dbname)
        if options["delete"]:
            OKMUService.objects.all().delete()
        self.load_okmu(cache_settings=qmsdb.settings)

    def load_okmu(self, cache_settings):
        """
        Загрузка справочников ОКМУ из qms
        """
        qms = QMS(cache_settings)
        query = qms.query
        for level in range(1, 5):
            query.execute_query('LoadOKMU', cache_settings['DATABASE_CODE'], level)
            for service_fields_list in query.results():
                code = service_fields_list[0]
                name = service_fields_list[1]
                parent = service_fields_list[2]
                service_type = service_fields_list[3]
                settings = service_fields_list[4]
                is_finished = (level >= 4)
                try:
                    parent_obj = OKMUService.objects.get(code=parent)
                except OKMUService.DoesNotExist:
                    parent_obj = None
                if code and name:
                    try:
                        okmu_obj = OKMUService.objects.get(code=code)
                    except OKMUService.DoesNotExist:
                        okmu_obj = OKMUService(code=code)
                    okmu_obj.level = level
                    okmu_obj.is_finished = is_finished
                    okmu_obj.name = name
                    okmu_obj.parent = parent_obj
                    if service_type:
                        okmu_obj.type = service_type
                    if settings:
                        okmu_obj.settings = jsonload(settings)
                    okmu_obj.save()

