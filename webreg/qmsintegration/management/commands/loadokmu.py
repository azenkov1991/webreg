from json import loads as jsonload
from django.core.management.base import BaseCommand, CommandError
from main.models import Service
from qmsmodule.qmsfunctions import *
from qmsintegration.models import *


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("dbname", help="Название настроек базы QMS из qmsintegration.OmsDB")
        parser.add_argument("-u", "--update", help="Только обновление существующих услуг", action="store_true")

    def handle(self, *args, **options):
        dbname = options["dbname"]
        try:
            qmsdb = QmsDB.objects.get(name=dbname)
        except models.ObjectDoesNotExist:
            raise CommandError("Нет описания базы данных Qms с именем " + dbname)
        if options["update"]:
            self.stdout.write("Updating services...")
            self.load_okmu(qmsdb, True)
        else:
            self.load_okmu(qmsdb, False)

    def get_parent(self, code, clinic):
        try:
            parent = Service.objects.get(code=code, clinic=clinic)
        except Service.DoesNotExist:
            parent = None
        return parent

    def get_okmu_type(self, list):
        try:
            return list[3]
        except:
            return None

    def get_okmu_settings(self, list):
        try:
            return jsonload(list[4])
        except:
            return None

    def load_okmu(self, qmsdb, update_only):
        """
        Загрузка справочников ОКМУ из qms
        """
        qms = QMS(qmsdb.settings)
        clinic = qmsdb.clinic
        query = qms.query
        for level in range(1, 5):
            query.execute_query('LoadOKMU', qmsdb.settings['DATABASE_CODE'], level)
            for service_fields_list in query.results():
                code = service_fields_list[0]
                name = service_fields_list[1]
                if code and name:
                    parent = self.get_parent(service_fields_list[2], clinic)
                    is_finished = (level >= 4)
                    type = self.get_okmu_type(service_fields_list)
                    settings = self.get_okmu_settings(service_fields_list)
                    if update_only and is_finished:
                        Service.objects.filter(code=code, clinic=clinic).update(
                            level=level,
                            is_finished=is_finished,
                            name=name,
                            parent=parent,
                            type=type,
                            settings=settings
                        )
                    else:
                        Service.objects.update_or_create(
                            defaults={
                                'level': level,
                                'is_finished': is_finished,
                                'name': name,
                                'parent': parent,
                                'type': type,
                                'settings': settings
                            },
                            code=code, clinic=clinic
                        )[0].save()



