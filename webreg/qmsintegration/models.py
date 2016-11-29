from django.db import models
from django.contrib.postgres.fields import JSONField


QMS_OBJECT_PREFIX = 'qqc'


class QmsDB(models.Model):
    name = models.CharField(max_length=128, verbose_name="Название")
    connection_param = JSONField(verbose_name="Настройки соединения")
    db_code = models.CharField(max_length=128, verbose_name="Код основной базы данных")
    coding = models.CharField(max_length=16, verbose_name="Кодировка базы данных")
    clinic = models.ForeignKey('main.Clinic', verbose_name="Мед. учреждение")

    @property
    def settings(self):
        return {
            'CONNECTION_PARAM': self.connection_param,
            'CACHE_CODING': self.coding,
            'DATABASE_CODE': self.db_code
        }

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "База данных QMS"
        verbose_name_plural = "Базы данных QMS"


class ObjectMatchingTable(models.Model):
    internal_name = models.CharField(max_length=128, verbose_name='Имя таблицы', unique=True)
    external_name = models.CharField(max_length=128, verbose_name='Имя во внешней системе', unique=True)

    class Meta:
        verbose_name_plural = 'Таблица соответсвий объектов '


class IdMatchingTable(models.Model):
    internal_id = models.IntegerField(verbose_name='ID сущности')
    external_id = models.CharField(max_length=128, verbose_name='ID во внешней системе')
    object_matching_table = models.ForeignKey(ObjectMatchingTable)

    class Meta:
        unique_together = ('internal_id', 'object_matching_table')
        verbose_name_plural = 'Таблица соответсвий id'


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


def delete_external_ids(models):
    for model in models:
        object_name = model._meta.label
        object_id = model.id
        IdMatchingTable.objects.filter(internal_id=object_id,
                                       object_matching_table__internal_name=object_name).delete()


def set_external_id(model, qmsObj, qqc):
    internal_name = model._meta.label
    internal_id = model.id
    try:
        omt = ObjectMatchingTable.objects.get(internal_name=internal_name, external_name=qmsObj)
    except models.ObjectDoesNotExist:
        omt = ObjectMatchingTable(internal_name=internal_name, external_name=qmsObj)
        omt.save()
    try:
        IdMatchingTable.objects.get(internal_id=internal_id, external_id=qqc,
                                          object_matching_table_id=omt.id)
    except models.ObjectDoesNotExist:
        imt = IdMatchingTable(internal_id=internal_id, external_id=qqc,
                              object_matching_table_id=omt.id)
        imt.save()


def get_external_id(model):
    internal_name = model._meta.label
    internal_id = model.id
    try:
        imt = IdMatchingTable.objects.get(internal_id=internal_id, object_matching_table__internal_name=internal_name)
    except models.ObjectDoesNotExist:
        return 0
    return imt.external_id

def get_internal_id(external_id, qmsObj):
    imt = IdMatchingTable.objects.get(external_id=external_id, object_matching_table__external_name=qmsObj)
    return imt.internal_id

def entity_exist(qmsObj, qqc):
    """
    Проверяет загружен ли уже объект из qms
    :param qmsObj:
    :param qqc:
    :return: True or False
    """
    if IdMatchingTable.objects.filter(external_id=qqc, object_matching_table__external_name=qmsObj).exists():
        return True
    else:
        return False
