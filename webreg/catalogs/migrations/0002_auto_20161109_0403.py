# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-09 04:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogs', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mkbdiagnos',
            name='name',
            field=models.CharField(max_length=1024, verbose_name='Название'),
        ),
    ]
