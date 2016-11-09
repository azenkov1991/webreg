# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-09 03:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LogModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True)),
                ('time', models.TimeField(auto_now_add=True)),
                ('level', models.CharField(db_index=True, max_length=256, verbose_name='Уровень')),
                ('logger_name', models.CharField(max_length=256, verbose_name='Логгер')),
                ('source_file', models.CharField(max_length=1024, verbose_name='Источник')),
                ('message', models.TextField(verbose_name='Сообщение')),
            ],
        ),
    ]
