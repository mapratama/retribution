from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0003_booking_platform'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='review',
            field=models.TextField(blank=True, default=b''),
        ),
    ]
