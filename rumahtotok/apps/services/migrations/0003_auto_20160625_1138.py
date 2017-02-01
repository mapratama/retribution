# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-25 04:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0002_service_discounted_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service',
            name='name',
            field=models.CharField(max_length=255, verbose_name=b'Name'),
        ),
        migrations.AlterUniqueTogether(
            name='service',
            unique_together=set([('treatment', 'name')]),
        ),
    ]
