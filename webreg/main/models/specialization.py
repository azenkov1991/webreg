from django.db import models


class Specialization(models.Model):
    name = models.CharField(
        max_length=128, verbose_name='Специализация',
        blank=True, null=True
    )

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'main'
        verbose_name = "Специализация"
        verbose_name_plural = "Специализации"
