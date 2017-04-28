from django.db import models


class SiteConfig(models.Model):
    site = models.OneToOneField('sites.Site')
    login_url = models.CharField(
        max_length=512,
        verbose_name='Страница аутентификации'
    )

    class Meta:
        verbose_name = "Настройки сайта"
        verbose_name_plural = "Настройки сайтов"
