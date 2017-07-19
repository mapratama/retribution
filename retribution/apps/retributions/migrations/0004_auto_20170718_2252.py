# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-07-18 15:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('retributions', '0003_auto_20170705_1413'),
    ]

    operations = [
        migrations.AddField(
            model_name='retribution',
            name='email',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='retribution',
            name='has_submitted',
            field=models.BooleanField(default=False),
        ),
    ]
