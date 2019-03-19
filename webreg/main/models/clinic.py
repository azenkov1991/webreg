from django.db import models


class Clinic(models.Model):
    name = models.CharField(
        max_length=128, verbose_name="Наименование мед. учреждения"
    )
    city = models.CharField(
        max_length=128, verbose_name="Город"
    )
    address = models.CharField(
        max_length=256, verbose_name="Адрес"
    )
    index_address = models.CharField(max_length=31, verbose_name='Индекс')
    email = models.EmailField(verbose_name='Электронная почта')
    picture = models.ImageField(
        verbose_name='Фотография', null=True
    )

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'main'
        verbose_name = "Мед. уреждение"
        verbose_name_plural = "Мед. учреждения"
