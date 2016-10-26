from django.db import models


class LogModel(models.Model):
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    level = models.CharField(max_length=256, verbose_name="Уровень", db_index=True)
    source_file = models.CharField(max_length=1024, verbose_name="Источник")
    message = models.TextField(verbose_name="Сообщение")





