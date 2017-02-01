# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-04 08:11
from __future__ import unicode_literals

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('orders', '0006_order_unique_price'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentConfirmation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False)),
                ('status', models.PositiveSmallIntegerField(choices=[(1, b'New'), (2, b'Accepted'), (3, b'Rejected')], default=1)),
                ('photo_url', models.CharField(max_length=255)),
                ('value', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('notes', models.TextField(blank=True, default=b'')),
                ('correction_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payment_confirmations', to=settings.AUTH_USER_MODEL)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payment_confirmations', to='orders.Order')),
            ],
        ),
        migrations.RemoveField(
            model_name='orderconfirmation',
            name='correction_by',
        ),
        migrations.RemoveField(
            model_name='orderconfirmation',
            name='order',
        ),
        migrations.DeleteModel(
            name='OrderConfirmation',
        ),
    ]
