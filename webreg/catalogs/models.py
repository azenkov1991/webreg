# -*- coding: utf-8 -*-
from django.db import models


class MKBDiagnos(models.Model):
    code = models.CharField(
        max_length=32, verbose_name="Код МКБ"
    )
    name = models.CharField(
        max_length=1024, verbose_name="Название"
    )
    is_finished = models.BooleanField(
        verbose_name="Является диагнозом"
    )
    level = models.IntegerField(
        verbose_name="Уровень"
    )
    parent = models.ForeignKey(
        'self', blank=True, null=True
    )

    def __str__(self):
        return self.code + " " + self.name

    class Meta:
        verbose_name = "МКБ"
        verbose_name_plural = "МКБ"
        ordering = ["code"]



