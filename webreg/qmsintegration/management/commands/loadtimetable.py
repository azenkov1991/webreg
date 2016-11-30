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
        parser.add_argument("qmsdepartment", help="Идентификатор подразделения в QMS")
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

    def find_cell(self, date, specialist, time_start, time_end, slot_type, cabinet, okmu_list, department, except_if_not_exist):
        try:
            cell = Cell.objects.get(date=date, specialist_id=specialist.id, time_start=time_start, time_end=time_end)
        except Cell.DoesNotExist:
            if except_if_not_exist:
                return None
            else:
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
        if not options["qmsdepartment"]:
            raise CommandError("Необходимо задать наименование подразделения в qMS")
        qms_dep = options["qmsdepartment"]
        if options["specialist"]:
            specialists = Specialist.objects.filter(pk=options["specialist"])
            department = specialists[0].department
        if options["department"]:
            department_id = options["department"]
            try:
                department = Department.objects.get(pk=department_id)
                CmdSpec().load_specs_in_department(qms=qms, department=department, qms_department=qms_dep)
            except models.ObjectDoesNotExist:
                raise CommandError("Нет подразделения с id = " + department_id)
            specialists = Specialist.objects.filter(department_id=department.id)
        if specialists == None:
            raise CommandError("Необходимо задать специалиста или подразделение со специалистами")

        for specialist in specialists:
            qqc244 = get_external_id(specialist)
            cells = qms.get_timetable(qqc244, date_from, date_to)
            local_cells = [c for c in Cell.objects.filter(date__range=[date_from, date_to], specialist_id=specialist.id)] # получаем все ячейки за заданный период по заданному спецу, которые лежат в базе
            # дальше мы перебираем ячейки из qMS. Но если в qMS удалят ячейку, то мы ее не обойдем в цикле. Чтобы не "забыть" про такие ячейки, мы получаем все ячейки из нашей базы, сохраняем их в списке.
            # И те, которые были обработаны, удаляются из списка. Оставшиеся в списке обрабатываются согласно логике программы (удаляются, если на них не производилась запись)
            for cell_item in cells:
                kwargs = {'date': cell_item.date, 'specialist': specialist, 'time_start': cell_item.time_start,
                          'time_end': cell_item.time_end, 'slot_type': cell_item.slot_type,
                          'cabinet': cell_item.cabinet, 'okmu_list': cell_item.okmu_list,
                          'department': department}
                cell = self.find_cell(except_if_not_exist=True, **kwargs)
                if cell == None: # если ячейки у нас еще нет
                    if (cell_item.date >= datetime.datetime.now().date()) and (cell_item.free == "1"): # а дата этой ячейки не в прошлом и она не занята
                        self.find_cell(except_if_not_exist=False, **kwargs) # создаем ее. local_cells не трогаем, т.к. там этой ячейки не может быть
                        # если дата ячейки в прошлом, ячейки не было и она появилась в qMS, то незачем ее грузить
                else: # если ячейка уже добавлена
                    if (cell.date >= datetime.datetime.now().date()) or (cell.appointment_set.exists()): # если дата ячейки не в прошлом или на эту ячейку была произведена запись
                        local_cells.remove(cell) # удаляем эту ячейку из кандидатов на "удаление"
                    # если дата ячейки в прошлом и на нее была произведена запись, то ячейку нужно удалить
            for cell in local_cells: # удаляем кандидатов на удаление
                if (not cell.appointment_set.exists()): # если, конечно, на них не производилась запись
                    cell.delete()










