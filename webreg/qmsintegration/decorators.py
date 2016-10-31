from qmsintegration.models import *

QMS_OBJECT_PREFIX = 'qqc'


def get_external_variables(dic):
    """
        Принимает словарь переменных {'имя':значение}
        Если у переменной есть атрибут _meta.label найдет соответствие в MatchingTable
    :return:
        Возвращает словарь соответсвий из MatchingTable
        Дрбавляет к именам из таблицы соответсвий объектов QMS_OBJECT_PREFIX
    """
    matching_dict = {}
    for (key, value) in dic.items():
        if hasattr(value, '_meta'):
            meta = value._meta
            if hasattr(meta, 'label'):
                try:
                    omt = ObjectMatchingTable.objects.get(internal_name=meta.label)
                    imt = IdMatchingTable.objects.get(internal_id=value.id, object_matching_table_id=omt.id)
                    object_name = QMS_OBJECT_PREFIX + omt.external_name
                    matching_dict.update({object_name: imt.external_id})
                except models.ObjectDoesNotExist:
                   pass
    return matching_dict





