# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-30 13:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BalanceUpdate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.PositiveSmallIntegerField(choices=[(1, b'Order'), (2, b'Manual'), (3, b'Referral')])),
                ('status', models.PositiveSmallIntegerField(choices=[(1, b'Created'), (2, b'Canceled')], default=1)),
                ('value', models.IntegerField()),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False)),
                ('notes', models.TextField(blank=True, default=b'')),
            ],
        ),
    ]
