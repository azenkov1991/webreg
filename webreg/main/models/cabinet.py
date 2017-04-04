from django.db import models


class Cabinet(models.Model):
    number = models.PositiveIntegerField(
        verbose_name="Номер кабинета", null=True
    )
    name = models.CharField(
        max_length=128, verbose_name="Название"
    )
    department = models.ForeignKey(
        'main.Department', verbose_name="Подразделение"
    )

    def __str__(self):
        return "Кабинет " + str(self.number)

    class Meta:
        app_label = 'main'
        verbose_name = "Кабинет"
        verbose_name_plural = "Кабинеты"
