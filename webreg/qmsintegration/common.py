from datetime import date, time
from main.models import Cell, SlotType, Cabinet
from catalogs.models import OKMUService
from qmsmodule.qmsfunctions import QMS
from qmsintegration.models import get_external_id



def update_specialist_timetable(specialist, date_from, date_to, qms):
    """
    Функция обновляет расписание из qms специалиста
    :param specialist:
    :param date_from:
    :param date_to:
    :param qms:
    :return:
    """
    qqc244 = get_external_id(specialist)
    qms_cells = qms.get_timetable(qqc244, date_from, date_to)
    # получаем все ячейки за заданный период по заданному спецу, которые лежат в базе, к которым нет назначения
    local_cells_not_appointed = Cell.objects.filter(date__range=[date_from, date_to],date__gte=date.today(),
                        specialist_id=specialist.id,
                        appointment__isnull = True)
    # к которым eсть назначения
    local_cells_appointed = Cell.objects.filter(date__range=[date_from, date_to],
                                                specialist_id=specialist.id,
                                                appointment__isnull=False)
    # удаление всех ячеек к которым не было назначений
    local_cells_not_appointed.delete()
    for qms_cell in qms_cells:
        # для каждой ячейки на которую было сделано назначение удаляем из полученных,
        # так как если была запись то не редактируем
        try:
            local_cells_appointed.get(date=qms_cell.date,
                                                       time_start=qms_cell.time_start,
                                                       time_end=qms_cell.time_end)
            qms_cells.remove(qms_cell)
        except Cell.DoesNotExist:
            pass

    # записываем все оставшиеся полученные свободные ячейки
    for qms_cell in qms_cells:
        if qms_cell.free and  \
            qms_cell.time_start!=time(0,0)and \
            qms_cell.date >= date.today():

            cell = Cell(
                date=qms_cell.date,
                specialist_id=specialist.id,
                time_start=qms_cell.time_start, time_end=qms_cell.time_end
            )
            cell.slot_type = SlotType.objects.get_or_create(name=qms_cell.slot_type)[0]
            if qms_cell.cabinet:
                cabinet = Cabinet.objects.get_or_create(number=qms_cell.cabinet, department=specialist.department)[0]
                if not cabinet.name:
                    cabinet.name = "Кабинет № " + str(qms_cell.cabinet)
                cell.cabinet = cabinet
            cell.save()
            for okmu in qms_cell.okmu_list:
                cell.performing_services.add(OKMUService.objects.get_or_create(code=okmu,is_finished=1,level=5)[0])




