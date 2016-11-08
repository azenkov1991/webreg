import  logging
from django.core.management.base import BaseCommand, CommandError
from qmsmodule.qmsfunctions import *
from qmsintegration.models import *
from main.models import Specialist, Department

logger = logging.getLogger("webreg")


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("dbname", help="Название настроек базы QMS из qmsintegration.OmsDB")
        parser.add_argument("pID", help="Подраздление в QMS")
        parser.add_argument("department", help="Id подразделения", type=int)
        parser.add_argument("-d", "--delete", help="Перед загрузкой все специалисты будут удалены",
                            action="store_true", dest="delete")

    def handle(self, *args, **options):
        dbname = options["dbname"]
        department_id = options["department"]
        try:
            qmsdb = QmsDB.objects.get(name=dbname)
        except models.ObjectDoesNotExist:
            raise CommandError("Нет описания базы данных Qms с именем " + dbname)
        try:
            department = Department.objects.get(pk=department_id)
        except models.ObjectDoesNotExist:
            raise CommandError("Нет подразделения с id = " + department_id)
        if options["delete"]:
            specialists = Specialist.objects.filter(department_id=department.id)
            delete_external_ids(specialists)


        qms = QMS(qmsdb.settings)
        specialists = qms.get_all_doctors(options["pID"])
        for spec in specialists:
            fio = spec['firstName'] + " " + spec['lastName'] + ' ' + spec['middleName']
            if not spec.IsActive:
                continue
            if entity_exist("244", spec.qqc244):
               logger.info("Специалист уже существует " + spec.qqc244 + ' ' + fio)
               continue

            specialist = Specialist(fio=fio, specialization=spec['specialization'], department_id=department_id)
            try:
                specialist.save()
                set_external_id(specialist, "244", spec.qqc244)
            except Exception as ex:
                logger.error("Не удалось загрузить специалиста из qms " + spec.qqc244 + ' ' + fio + "\n" +
                             str(ex))



