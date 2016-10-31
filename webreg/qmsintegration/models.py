from django.db import models


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
