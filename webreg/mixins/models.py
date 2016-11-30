# -*- coding: utf-8 -*-
from django.db import models


class TimeStampedModel(models.Model):
    created = models.DateTimeField(auto_now_add=True, verbose_name='Системная дата создания')
    modified = models.DateTimeField(auto_now=True, verbose_name='Системная дата изменения')

    def __str__(self):
        return 'TimeStampedModel'

    class Meta:
        abstract = True


class ActiveMixin(models.Model):
    is_active = models.BooleanField(verbose_name="Активно", default=True)

    class Meta:
        abstract = True
