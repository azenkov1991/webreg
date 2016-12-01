# -*- coding: utf-8 -*-
from django.db import models
from django.utils.timezone import now


class TimeStampedModel(models.Model):
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='Системная дата создания')
    modified_time = models.DateTimeField(auto_now=True, verbose_name='Системная дата изменения')

    def __str__(self):
        return 'TimeStampedModel'

    class Meta:
        abstract = True


class ActiveManager(models.Manager):
    def get_queryset(self):
        return super(ActiveManager, self).get_queryset().filter(deleted=False)


class DeletedManager(models.Manager):
    def get_queryset(self):
        return super(DeletedManager, self).get_queryset().filter(deleted=True)


class SafeDeleteMixin(models.Model):
    deleted_time = models.DateTimeField(verbose_name='Системная дата удаления', null=True, blank=True)
    deleted = models.BooleanField(verbose_name="Удален", default=False)
    objects = ActiveManager()
    deleted_objects = DeletedManager()
    all_objects = models.Manager()

    def safe_delete(self):
        self.deleted_time = now()
        self.deleted = True
        self.save()

    def undelete(self):
        self.deleted_time = None
        self.deleted = False
        self.save()

    class Meta:
        abstract = True
