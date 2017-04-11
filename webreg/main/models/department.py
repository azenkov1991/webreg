from django.db import models
from mixins.models import SafeDeleteMixin

class Department(SafeDeleteMixin):
    name = models.CharField(
        max_length=128, verbose_name="Название подразделения"
    )
    parent_department = models.ForeignKey(
        'self', blank=True, null=True
    )
    clinic = models.ForeignKey(
        'main.Clinic', verbose_name="Мед. учреждение"
    )

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'main'
        verbose_name = "Подразделение"
        verbose_name_plural = "Подразделения"
