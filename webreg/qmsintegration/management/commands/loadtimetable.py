import  logging
from datetime import date, datetime
from django.core.management.base import BaseCommand, CommandError
from qmsmodule.qmsfunctions import *
from qmsintegration.models import *
from main.models import Specialist, Department, Cell, Cabinet, SlotType
from catalogs.models import OKMUService
from qmsintegration.management.commands.loadspecialists import Command as CmdSpec

logger = logging.getLogger("webreg")


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("dbname", help="Название настроек базы QMS из qmsintegration.OmsDB")
        parser.add_argument("dateFrom", help="Дата от в формате yyyy-mm-dd")
        parser.add_argument("dateTo", help="Дата до в формате yyyy-mm-dd")
        parser.add_argument("--department", dest="department", help="Id подразделения", type=int)
        parser.add_argument("--specialist", dest="specialist", help="Id специалиста", type=int)

    def get_cabinet(self, cab_num, department):
        try:
            int_cab_num = int(cab_num)
            cabinet_number = "Кабинет № " + str(int_cab_num)
        except:
            return None
        try:
            return Cabinet.objects.get(number=int_cab_num, department=department)
        except Cabinet.DoesNotExist:
            cabinet = Cabinet(name=cabinet_number, department=department,
                              number=int_cab_num)
            cabinet.save()
            return cabinet

    def get_slot_type(self, slot_type, department):
        try:
            slot = SlotType.objects.get(name=slot_type, clinic=department.clinic)
        except SlotType.DoesNotExist:
            slot = SlotType(name=slot_type, clinic=department.clinic)
        slot.save()
        return slot

    def get_localdb_cells(self, date_from, date_to, specialist):
        cell_list = []
        for date in daterange(date_from, date_to):
            queryset = Cell.objects.filter(date=date, specialist_id=specialist.id)
            for cell in queryset:
                cell_list.append(cell)
        return cell_list

    def get_usl(self, okmu):
        if okmu:
            if 'None' != okmu:
                try:
                    obj = OKMUService.objects.get(code=okmu)
                except models.ObjectDoesNotExist:
                    obj = OKMUService(code=okmu, is_finished=True, level=5)
                obj.save()
                return obj
        return None

    def find_cell(self, date, specialist, time_start, time_end, slot_type, cabinet, okmu_list, department):
        try:
            cell = Cell.objects.get(date=date, specialist_id=specialist.id, time_start=time_start, time_end=time_end)
        except Cell.DoesNotExist:
            cell = Cell(date=date, specialist_id=specialist.id, time_start=time_start, time_end=time_end)
        cell.cabinet = self.get_cabinet(cab_num=cabinet, department=department)
        if not slot_type:
            slot_type = ''
        cell.slot_type = self.get_slot_type(slot_type=slot_type, department=department)
        cell.save()
        okmus = [okmu for okmu in cell.performing_services.all()]
        for okmu in okmu_list:
            if okmu in okmus:
                okmus.remove(okmu)
            else:
                usl = self.get_usl(okmu=okmu)
                if usl:
                    cell.performing_services.add(usl)
        for okmu in okmus:
            cell.performing_services.remove(okmu)
        cell.save()
        return cell

    def handle(self, *args, **options):
        dbname = options["dbname"]
        try:
            qmsdb = QmsDB.objects.get(name=dbname)
        except models.ObjectDoesNotExist:
            raise CommandError("Нет описания базы данных Qms с именем " + dbname)

        try:
            date_from = datetime.datetime.strptime(options["dateFrom"], "%Y-%m-%d").date()
            date_to = datetime.datetime.strptime(options["dateTo"], "%Y-%m-%d").date()
        except Exception:
            raise CommandError("Неверный формат даты")

        specialists = None
        department = None
        qms = QMS(qmsdb.settings)
        if options["specialist"]:
            specialists = Specialist.objects.filter(pk=options["specialist"])
            department = specialists[0].department
        if options["department"]:
            department_id = options["department"]
            try:
                department = Department.objects.get(pk=department_id)
                CmdSpec().load_specs_in_department(qms=qms, department=department)
            except models.ObjectDoesNotExist:
                raise CommandError("Нет подразделения с id = " + department_id)
            specialists = Specialist.objects.filter(department_id=department.id)
        if specialists == None:
            raise CommandError("Необходимо задать специалиста или подразделение со специалистами")

        for specialist in specialists:
            qqc244 = get_external_id(specialist)
            cells = qms.get_timetable(qqc244, date_from, date_to)
            local_cells = self.get_localdb_cells(date_from=date_from, date_to=date_to, specialist=specialist)
            for cell_item in cells:
                # если есть ячейка у специалиста на это время без назначения удалить
                cell = self.find_cell(date=cell_item.date, specialist=specialist, time_start=cell_item.time_start,
                                      time_end=cell_item.time_end, slot_type=cell_item.slot_type,
                                      cabinet=cell_item.cabinet, okmu_list = cell_item.okmu_list,
                                      department=department)
                if cell in local_cells:
                    if cell.date >= datetime.datetime.now().date():
                        local_cells.remove(cell)
                    else:
                        if cell.appointment_set.exists():
                            local_cells.remove(cell)
            for cell in local_cells:
                cell.remove()










