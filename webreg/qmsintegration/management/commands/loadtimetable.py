import  logging
from datetime import date, datetime
from django.core.management.base import BaseCommand, CommandError
from qmsmodule.qmsfunctions import *
from qmsintegration.models import *
from qmsintegration.common import update_specialist_timetable
from main.models import Specialist, Department, Cell, Cabinet, SlotType, Service
from qmsintegration.management.commands.loadspecialists import Command as CmdSpec

logger = logging.getLogger("command_manage")


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("dbname", help="Название настроек базы QMS из qmsintegration.OmsDB")
        parser.add_argument("--dateFrom", help="Дата от в формате yyyy-mm-dd")
        parser.add_argument("--dateTo", help="Дата до в формате yyyy-mm-dd")
        parser.add_argument("--department", dest="department", help="Id подразделения", type=int)
        parser.add_argument("--specialist", dest="specialist", help="Id специалиста", type=int)
        parser.add_argument("--slottype", dest="slottype", help="Загружать только выбранный тип слота")

    def handle(self, *args, **options):
        dbname = options["dbname"]
        try:
            qmsdb = QmsDB.objects.get(name=dbname)
        except models.ObjectDoesNotExist:
            raise CommandError("Нет описания базы данных Qms с именем " + dbname)

        if options['dateFrom']:
            try:
                date_from = datetime.datetime.strptime(options["dateFrom"], "%Y-%m-%d").date()
            except ValueError:
                raise CommandError("Неверный формат даты от")
        else:
            date_from = datetime.datetime.today().date()

        if options['dateTo']:
            try:
                date_to = datetime.datetime.strptime(options["dateTo"], "%Y-%m-%d").date()
            except ValueError:
                raise CommandError("Неверный формат даты до")
        else:
            date_to = date_from + datetime.timedelta(14)

        specialists = None
        department = None
        slot_type = options['slottype']
        qms = QMS(qmsdb.settings)

        if options["specialist"]:
            specialists = Specialist.objects.filter(pk=options["specialist"])
            department = specialists[0].department
        elif options["department"]:
            department_id = options["department"]
            try:
                department = Department.objects.get(pk=department_id)
            except models.ObjectDoesNotExist:
                raise CommandError("Нет подразделения с id = " + department_id)
            specialists = Specialist.objects.filter(department_id=department.id)
        else:
            specialists = Specialist.objects.filter(
                department__clinic=qmsdb.clinic
            )

        if not specialists:
            raise CommandError("Необходимо задать специалиста или подразделение со специалистами")

        logger.info("Загрузка расписания с " + str(date_from) + "по " + str(date_to) + 'для учреждения ' + )

        for specialist in specialists:
            logger.info("Загрузка расписания специалиста" + str(specialist))
            update_specialist_timetable(specialist, date_from, date_to, qms, slot_type)










