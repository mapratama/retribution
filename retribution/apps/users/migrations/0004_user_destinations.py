# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-07-14 13:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('destinations', '0001_initial'),
        ('users', '0003_remove_user_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='destinations',
            field=models.ManyToManyField(blank=True, related_name='users', to='destinations.Destination'),
        ),
    ]