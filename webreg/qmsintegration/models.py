from django.db import models
from django.contrib.postgres.fields import JSONField
from main.models import Clinic


class QmsDB(models.Model):
    name = models.CharField(max_length=128, verbose_name="Название")
    connection_param = JSONField(verbose_name="Настройки соединения")
    db_code = models.CharField(max_length=128, verbose_name="Код основной базы данных")
    coding = models.CharField(max_length=16, verbose_name="Кодировка базы данных")
    clinic = models.ForeignKey(Clinic, verbose_name="Мед. учреждение")

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


