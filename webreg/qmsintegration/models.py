import logging
from main.models import *
from django.db import models
from django.contrib.postgres.fields import JSONField
from django.db.models.signals import post_delete
from constance import config


log = logging.getLogger("webreg")
QMS_OBJECT_PREFIX = 'qqc'


class QmsIntegrationError(Exception):
    pass


class QmsDB(models.Model):
    clinic = models.OneToOneField(
        'main.Clinic', verbose_name="Мед. учреждение"
    )
    name = models.CharField(
        max_length=128, verbose_name="Название"
    )
    host = models.CharField(
        max_length=128, verbose_name="Адрес хоста",
        default="localhost"
    )
    user = models.CharField(
        max_length=128, verbose_name="Пользователь",
        default="_SYSTEM"
    )
    password = models.CharField(
        max_length=128, verbose_name="Пароль",
        default="SYS"
    )
    port = models.PositiveIntegerField(
        verbose_name="Порт", default=1972
    )

    wsdl_port = models.PositiveIntegerField(
        verbose_name="Порт wsdl", default=57772
    )

    namespace = models.CharField(
        max_length=32, verbose_name="Namespace",
        default="QMS"
    )

    db_code = models.CharField(
        max_length=128, verbose_name="Код основной базы данных"
    )
    coding = models.CharField(
        max_length=16, verbose_name="Кодировка базы данных"
    )

    cre293 = models.BooleanField(
        default=True, verbose_name="Создавать источник финансирования?"
    )

    update_phone = models.BooleanField(
        default=True, verbose_name="Обновлять номер телефона пациента?"
    )

    @property
    def settings(self):
        return {
            'CONNECTION_PARAM': {
                'host': self.host,
                'port': str(self.port),
                'wsdl_port': str(self.wsdl_port),
                'user': self.user,
                'password': self.password,
                'namespace': self.namespace,
            },
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
    user_profile = models.ForeignKey(
        'main.UserProfile', verbose_name="Профиль пользователя"
    )

    qmsdb = models.ForeignKey(
        QmsDB, verbose_name="База Qms"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Пользователь qms"
        verbose_name_plural = "Пользователи qms"
        unique_together = ('user_profile', 'qmsdb',)


class QmsDepartment(models.Model):
    department = models.OneToOneField('main.Department')
    EPISODE_TYPE_CHOICES = (
        (1, "АМБУЛАТОРНО"),
        (2, "СТОМАТОЛОГИЯ")
    )
    episode_type = models.IntegerField(
        verbose_name="Тип эпизода", default=1, choices=EPISODE_TYPE_CHOICES
    )

    def __str__(self):
        return self.department.name

    class Meta:
        verbose_name = "Подразделение в qms"
        verbose_name_plural = "Подразделения в qms"


class QmsDepartmentCode(models.Model):
    qmsdepartament = models.ForeignKey(
        QmsDepartment, verbose_name='Департамент', related_name='codes'
    )
    code = models.CharField(
        max_length=31, verbose_name='Код'
    )

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = 'Код: '
        verbose_name_plural = 'Коды департаментов'
        unique_together = ('qmsdepartament', 'code')


class ObjectMatchingTable(models.Model):
    internal_name = models.CharField(max_length=128, verbose_name='Имя таблицы')
    external_name = models.CharField(max_length=128, verbose_name='Имя во внешней системе')

    def __str__(self):
        return self.internal_name + '->' + self.external_name

    class Meta:
        verbose_name_plural = 'Таблица соответсвий объектов '


class IdMatchingTable(models.Model):
    internal_id = models.IntegerField(verbose_name='ID сущности')
    external_id = models.CharField(max_length=128, verbose_name='ID во внешней системе')
    object_matching_table = models.ForeignKey(ObjectMatchingTable)

    class Meta:
        unique_together = ('internal_id', 'object_matching_table')
        verbose_name_plural = 'Таблица соответсвий id'


def delete_id_from_id_matching_table(sender, **kwargs):
    """
    Удаление кода Qms при удалеии объекта модели
    """
    if config.QMS_INTEGRATION_ENABLE:
        try:
            IdMatchingTable.objects.get(
                internal_id=kwargs['instance'].id,
                object_matching_table__internal_name=kwargs['instance']._meta.label
            ).delete()
        except IdMatchingTable.DoesNotExist:
            pass


def delete_object(sender, **kwargs):
    """
    Удаление объекта модели при удалении кода Qms
    """
    if config.QMS_INTEGRATION_ENABLE:
        instance_id = kwargs['instance'].internal_id
        instance_model = kwargs['instance'].object_matching_table.internal_name
        try:
            model_class = list(
                filter(
                    lambda x: hasattr(x, '_meta') and (x._meta.label == instance_model),
                    globals().values()
                )
            )[0]
            model_class.objects.filter(id=instance_id).delete()
        except:
            pass
        print(instance_model)
        print(instance_id)

try:
    post_delete.connect(delete_object, sender=IdMatchingTable)
    for obj_table in ObjectMatchingTable.objects.all():
        post_delete.connect(delete_id_from_id_matching_table, sender=obj_table.internal_name)
except:
    pass


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
        log.error("Ошибка интеграции с Qms. Не найден id: internal_id=" + str(internal_id) +
                  " model=" + internal_name)
        raise QmsIntegrationError
    return imt.external_id


def get_internal_id(qms_obj, external_id):
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
