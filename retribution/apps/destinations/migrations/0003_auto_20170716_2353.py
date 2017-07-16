# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-07-16 16:53
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('destinations', '0002_auto_20170716_2350'),
    ]

    operations = [
        migrations.AddField(
            model_name='destination',
            name='people_cost',
            field=models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0)], verbose_name=b'Harga Tiket'),
        ),
        migrations.AlterField(
            model_name='destination',
            name='bus_cost',
            field=models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0)], verbose_name=b'Tiket Bus'),
        ),
        migrations.AlterField(
            model_name='destination',
            name='micro_bus_cost',
            field=models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0)], verbose_name=b'Tiket Micro Bus'),
        ),
        migrations.AlterField(
            model_name='destination',
            name='mini_bus_cost',
            field=models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0)], verbose_name=b'Tiket Mini Bus'),
        ),
        migrations.AlterField(
            model_name='destination',
            name='motor_cost',
            field=models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0)], verbose_name=b'Tiket Motor'),
        ),
        migrations.AlterField(
            model_name='destination',
            name='sedan_cost',
            field=models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0)], verbose_name=b'Tiket Sedan'),
        ),
    ]
