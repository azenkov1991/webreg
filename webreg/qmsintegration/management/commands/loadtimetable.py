import  logging
from datetime import date
from django.core.management.base import BaseCommand, CommandError
from qmsmodule.qmsfunctions import *
from qmsintegration.models import *
from main.models import Specialist, Department, Cell, Cabinet
from catalogs.models import OKMUService

logger = logging.getLogger("webreg")


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("dbname", help="Название настроек базы QMS из qmsintegration.OmsDB")
        parser.add_argument("department", help="Id подразделения", type=int)
        parser.add_argument("dateFrom", help="Дата от в формате yyyy-mm-dd")
        parser.add_argument("dateTo", help="Дата до в формате yyyy-mm-dd")

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

        try:
            date_mas = options["dateFrom"].split("-")
            date_from = date(int(date_mas[0]), int(date_mas[1]), int(date_mas[2]))
            date_mas = options["dateTo"].split("-")
            date_to = date(int(date_mas[0]), int(date_mas[1]), int(date_mas[2]))
        except Exception:
            raise CommandError("Неверный формат даты")
        specialists = Specialist.objects.filter(department_id=department.id, IsActive=True)

        qms = QMS(qmsdb.settings)
        for specialist in specialists:
            qqc244 = get_external_id(specialist)
            cells = qms.get_timetable(qqc244, date_from, date_to)
            for cell_item in cells:
                cell = Cell()
                cell.date = cell_item.date
                cell.time_start = cell.time_start
                cell.time_end = cell.time_end
                cell.specialist = specialist
                try:
                    cabinet_number = int(cell_item.cabinet)
                    try:
                        cabinet = Cabinet.objects.get(number=cabinet_number, department_id=specialist.department.id)
                    except Cabinet.DoesNotExist:
                        cabinet_name = "Кабинет № " + cabinet_number
                        cabinet = Cabinet(number=cabinet_number, department_id=specialist.department.id,
                                          name=cabinet_name)
                        cabinet.save()
                    cell.cabinet = cabinet
                except ValueError:
                    pass
                for code in cell_item.okmu_list:
                    try:
                        service = OKMUService.objects.get(code=code)
                        cell.performing_services.add(service)
                    except OKMUService.DoesNotExist:
                        pass
                cell.save()









