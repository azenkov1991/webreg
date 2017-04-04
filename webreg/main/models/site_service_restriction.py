from django.db import models


class SiteServiceRestriction(models.Model):
    services = models.ManyToManyField(
        "catalogs.OKMUService", verbose_name="Услуга"
    )
    site = models.OneToOneField(
        "sites.Site", verbose_name="Сайт"
    )

    class Meta:
        app_label = 'main'
        verbose_name = "Разрашеение на назначение услуг на сайте"
        verbose_name_plural = "Разрешения на назначения услуг на сайтах"
