# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-30 13:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import rumahtotok.core.utils
import thumbnails.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('stores', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Therapist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', thumbnails.fields.ImageField(blank=True, help_text=b'Image must be 800x800 in dimension', upload_to=rumahtotok.core.utils.FilenameGenerator(prefix=b'therapist_photos'))),
                ('is_active', models.BooleanField(default=True)),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='therapists', to='stores.Store')),
            ],
        ),
    ]
