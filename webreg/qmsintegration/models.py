import logging
from django.db import models
from django.contrib.postgres.fields import JSONField


log = logging.getLogger("webreg")
QMS_OBJECT_PREFIX = 'qqc'


class QmsIntegrationError(Exception):
    pass


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


class QmsUser(models.Model):
    name = models.CharField(
        max_length=128, verbose_name="Имя пользователя"
    )
    qqc244 = models.CharField(
        max_length=256, verbose_name="qqc пользователя"
    )
    user_profile = models.OneToOneField('main.UserProfile')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Пользователь qms"
        verbose_name_plural = "Пользователи qms"


class ObjectMatchingTable(models.Model):
    internal_name = models.CharField(max_length=128, verbose_name='Имя таблицы')
    external_name = models.CharField(max_length=128, verbose_name='Имя во внешней системе')

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
                    try:
                        imt = IdMatchingTable.objects.get(internal_id=value.id, object_matching_table_id=omt.id)
                        object_name = QMS_OBJECT_PREFIX + omt.external_name
                        matching_dict.update({object_name: imt.external_id})
                    except IdMatchingTable.DoesNotExist:
                        log.error("Ошибка интеграции с Qms. Не найден id: internal_id="+value.id +
                                  " model=" + meta.label)
                        raise QmsIntegrationError
                except ObjectMatchingTable.DoesNotExist:
                    pass
    return matching_dict


def delete_external_ids(models):
    for model in models:
        object_name = model._meta.label
        object_id = model.id
        IdMatchingTable.objects.filter(internal_id=object_id,
                                       object_matching_table__internal_name=object_name).delete()


def set_external_id(model, qqc):
    internal_name = model._meta.label
    internal_id = model.id
    try:
        omt = ObjectMatchingTable.objects.get(internal_name=internal_name)
    except models.ObjectDoesNotExist:
        log.error("Попытка установки id объекта, отсутствующего в ObjectMatchingTable object = " + internal_name )
        raise QmsIntegrationError
    try:
        imt = IdMatchingTable.objects.get(internal_id=internal_id, external_id=qqc,
                                          object_matching_table_id=omt.id)
    except IdMatchingTable.DoesNotExist:
        imt = IdMatchingTable(internal_id=internal_id, external_id=qqc,
                              object_matching_table_id=omt.id)
        imt.save()


def get_external_id(model):
    internal_name = model._meta.label
    internal_id = model.id
    try:
        imt = IdMatchingTable.objects.get(internal_id=internal_id, object_matching_table__internal_name=internal_name)
    except models.ObjectDoesNotExist:
        log.error("Ошибка интеграции с Qms. Не найден id: internal_id=" + internal_id +
                  " model=" + internal_name)
        raise QmsIntegrationError
    return imt.external_id


def get_internal_id(external_id, qms_obj):
    try:
        imt = IdMatchingTable.objects.get(external_id=external_id, object_matching_table__external_name=qms_obj)
    except IdMatchingTable.DoesNotExist:
        raise QmsIntegrationError
    return imt.internal_id


def entity_exist(qms_obj, qqc):
    """
    Проверяет загружен ли уже объект из qms
    :param qms_obj:
    :param qqc:
    :return: True or False
    """
    if IdMatchingTable.objects.filter(external_id=qqc, object_matching_table__external_name=qms_obj).exists():
        return True
    else:
        return False
