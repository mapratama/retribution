# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-07-05 07:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('retributions', '0002_auto_20170523_2127'),
    ]

    operations = [
        migrations.AlterField(
            model_name='retribution',
            name='transport',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, b'Motor'), (2, b'Sedan'), (3, b'Mini Bus'), (4, b'Micro Bus'), (5, b'Bus')], null=True),
        ),
    ]
