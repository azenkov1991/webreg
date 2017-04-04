from django.db import models


class SlotType(models.Model):
    name = models.CharField(
        max_length=128, verbose_name="Имя", unique=True,
    )
    color = models.CharField(
        max_length=7, verbose_name="Цвет",
        help_text="HEX color, as #RRGGBB", blank=True, null=True
    )
    clinic = models.ForeignKey(
        'main.Clinic', verbose_name="Мед. учреждение"
    )
    def __str__(self):
        return self.name

    class Meta:
        app_label = 'main'
        verbose_name = "Тип слота"
        verbose_name_plural = "Типы слотов"
