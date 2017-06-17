from django.db import models


class Destination(models.Model):

    name = models.CharField(max_length=50)
    address = models.TextField()
    description = models.TextField(blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    long = models.FloatField(blank=True, null=True)

    def __unicode__(self):
        return self.name
