# -*- coding: utf-8 -*-
from django.db import models
from mixins.models import SafeDeleteMixin
from django.contrib.postgres.fields import JSONField


class Service(SafeDeleteMixin):
    clinic = models.ForeignKey(
        'main.Clinic', verbose_name="Мед. учреждение"
    )
    code = models.CharField(
        max_length=32, verbose_name="Код ОКМУ"
    )
    name = models.CharField(
        max_length=512, verbose_name="Название"
    )
    type = models.CharField(
        max_length=128, verbose_name="Тип", blank=True, null=True
    )
    settings = JSONField(
        verbose_name="Настройки", blank=True, null=True
    )
    parent = models.ForeignKey(
        'self', blank=True, null=True
    )
    is_finished = models.BooleanField(
        verbose_name="Является услугой",
        default=1
    )
    level = models.IntegerField(
        verbose_name="Уровень",
        default=4
    )

    def __str__(self):
        return self.code + " " + self.name

    class Meta:
        app_label = 'main'
        verbose_name = "Услугa"
        verbose_name_plural = "Услуги"
        ordering = ["code"]
