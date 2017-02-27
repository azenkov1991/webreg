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


class SafeDeleteQuerySet(models.query.QuerySet):
    def safe_delete(self):
        self.update(deleted_time=now(),
                    deleted=True)

    def undelete(self):
        self.update(deleted_time=None,
                    deleted=False)

class ActiveManager(models.manager.BaseManager.from_queryset(SafeDeleteQuerySet)):
    use_for_related_fields = True
    def get_queryset(self):
        return super().get_queryset().filter(deleted=False)


class DeletedManager(models.manager.BaseManager.from_queryset(SafeDeleteQuerySet)):
    def get_queryset(self):
        return super().get_queryset().filter(deleted=True)


class SafeDeleteMixin(models.Model):
    deleted_time = models.DateTimeField(verbose_name='Системная дата удаления', null=True, blank=True)
    deleted = models.BooleanField(verbose_name="Удален", default=False)
    objects = ActiveManager()
    deleted_objects = DeletedManager()
    all_objects = SafeDeleteQuerySet.as_manager()

    def safe_delete(self):
        self.deleted_time = now()
        self.deleted = True
        self.save()

    def undelete(self):
        self.deleted_time = None
        self.deleted = False
        self.save()

    def active(self):
        return not self.deleted
    active.boolean = True
    active.short_description="Активен"
    class Meta:
        abstract = True
