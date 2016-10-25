# -*- coding: utf-8 -*-
from django.db import models


class OKMUService(models.Model):
    code = models.CharField(max_length=32, primary_key=True, verbose_name="Код ОКМУ")
    name = models.CharField(max_length=256, verbose_name="Название")
    parent = models.ForeignKey('self', blank=True, null=True)

    def __str__(self):
        return self.code + " " + self.name

    class Meta:
        verbose_name = "Услугa"
        verbose_name_plural = "Услуги"
        ordering = ["code"]
