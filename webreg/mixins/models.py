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
    def get_queryset(self):
        return super(ActiveManager, self).get_queryset().filter(deleted=False)

    def get(self, *args, **kwargs):
        if ('pk' in kwargs) or ('id' in kwargs):
            return super().get_queryset().get(*args, **kwargs)

    def all_with_deleted(self):
        """ Return a queryset to every objects, including deleted ones. """
        queryset = SafeDeleteQuerySet(self.model, using=self._db)
        # We need to filter if we are in a RelatedManager. See the `test_related_manager`.
        if hasattr(self, 'core_filters'):
            # In a RelatedManager, must filter and add hints
            queryset._add_hints(instance=self.instance)
            queryset = queryset.filter(**self.core_filters)
        return queryset


class DeletedManager(models.manager.BaseManager.from_queryset(SafeDeleteQuerySet)):
    def get_queryset(self):
        return super(DeletedManager, self).get_queryset().filter(deleted=True)


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

    def _perform_unique_checks(self, unique_checks):
        errors = {}

        for model_class, unique_check in unique_checks:
            lookup_kwargs = {}
            for field_name in unique_check:
                f = self._meta.get_field(field_name)
                lookup_value = getattr(self, f.attname)
                if lookup_value is None:
                    continue
                if f.primary_key and not self._state.adding:
                    continue
                lookup_kwargs[str(field_name)] = lookup_value
            if len(unique_check) != len(lookup_kwargs):
                continue

            # This is the changed line
            if hasattr(model_class._default_manager, 'all_with_deleted'):
                qs = model_class._default_manager.all_with_deleted().filter(**lookup_kwargs)
            else:
                qs = model_class._default_manager.filter(**lookup_kwargs)

            model_class_pk = self._get_pk_val(model_class._meta)
            if not self._state.adding and model_class_pk is not None:
                qs = qs.exclude(pk=model_class_pk)
            if qs.exists():
                if len(unique_check) == 1:
                    key = unique_check[0]
                else:
                    key = models.base.NON_FIELD_ERRORS
                errors.setdefault(key, []).append(
                    self.unique_error_message(model_class, unique_check)
                )
        return errors
