from django.core.validators import MinValueValidator
from django.db import models


class Destination(models.Model):

    name = models.CharField(max_length=50)
    address = models.TextField()
    people_cost = models.FloatField('Harga Tiket', validators=[MinValueValidator(0)], default=0)
    motor_cost = models.FloatField('Tiket Motor', validators=[MinValueValidator(0)], default=0)
    sedan_cost = models.FloatField('Tiket Sedan', validators=[MinValueValidator(0)], default=0)
    mini_bus_cost = models.FloatField('Tiket Mini Bus', validators=[MinValueValidator(0)], default=0)
    micro_bus_cost = models.FloatField('Tiket Micro Bus', validators=[MinValueValidator(0)], default=0)
    bus_cost = models.FloatField('Tiket Bus', validators=[MinValueValidator(0)], default=0)
    description = models.TextField(blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    long = models.FloatField(blank=True, null=True)

    def __unicode__(self):
        return self.name
