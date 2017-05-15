from datetime import date, time
from main.models import Cell, SlotType, Cabinet
from catalogs.models import OKMUService
from qmsmodule.qmsfunctions import QMS
from qmsintegration.models import get_external_id


def update_specialist_timetable(specialist, date_from, date_to, qms, slot_type=None):
    """
    Функция обновляет расписание из qms специалиста
    :param specialist:
    :param date_from:
    :param date_to:
    :param qms:
    :param slot_type:
    :return:
    """
    qqc244 = get_external_id(specialist)
    qms_cells = qms.get_timetable(qqc244, date_from, date_to, slot_type)
    # получаем все ячейки за заданный период по заданному спецу, которые лежат в базе, к которым нет назначения
    local_cells_not_appointed = list(Cell.objects.filter(date__range=[date_from, date_to],date__gte=date.today(),
                                                         specialist_id=specialist.id,
                                                         appointment__isnull = True).values_list('id', flat=True))
    # к которым eсть назначения
    local_cells_not_free = Cell.objects.filter(date__range=[date_from, date_to],
                                               specialist_id=specialist.id,
                                               free=False)

    for qms_cell in qms_cells:
        # для каждой ячейки на которую было сделано назначение удаляем из полученных,
        # так как если была запись то не редактируем
        try:
            local_cells_not_free.get(date=qms_cell.date,
                                     time_start=qms_cell.time_start,
                                     time_end=qms_cell.time_end)
            qms_cells.remove(qms_cell)
        except Cell.DoesNotExist:
            pass

    # записываем все оставшиеся полученные свободные ячейки
    for qms_cell in qms_cells:
        if qms_cell.free and  \
           qms_cell.time_start != time(0,0)and \
           qms_cell.date >= date.today():
            slot_type = None
            if qms_cell.slot_type:
                slot_type = SlotType.objects.get_or_create(name=qms_cell.slot_type,
                                                           clinic_id=specialist.department.clinic.id)[0]
            cabinet = None
            if qms_cell.cabinet:
                try:
                    cabinet_number = int(qms_cell.cabinet)
                    cabinet_name = "Кабинет № " + str(qms_cell.cabinet)
                except ValueError:
                    cabinet_name = qms_cell.cabinet
                    cabinet_number = None

                cabinet = Cabinet.objects.update_or_create(name=cabinet_name,
                                                           number=cabinet_number,
                                                           department=specialist.department)[0]

            cell, created = Cell.objects.update_or_create(
                defaults={'cabinet':cabinet,
                          'slot_type':slot_type},
                date=qms_cell.date,
                specialist_id=specialist.id,
                time_start=qms_cell.time_start,
                time_end=qms_cell.time_end
            )
            if not created and cell.id in local_cells_not_appointed:
                local_cells_not_appointed.remove(cell.id)

            for service in cell.performing_services.all():
                if service.code not in qms_cell.okmu_list:
                    cell.performing_services.remove(service)
            for okmu in qms_cell.okmu_list:
                if okmu:
                    cell.performing_services.add(OKMUService.objects.get_or_create(code=okmu,is_finished=1,level=4)[0])

    # все оставшиеся ячейки к которым не было назначений удаляются
    Cell.objects.filter(id__in=local_cells_not_appointed).delete()



