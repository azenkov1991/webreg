# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2019-03-22 06:48
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('registration', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PatientRegistrationProfile',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('registration.registrationprofile',),
        ),
    ]