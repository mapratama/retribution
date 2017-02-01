from django.db import models

from thumbnails.fields import ImageField

from rumahtotok.core.utils import FilenameGenerator


class Treatment(models.Model):
    name = models.CharField(max_length=256)
    photo = ImageField(upload_to=FilenameGenerator(prefix='treatment'),
                       resize_source_to='source_300', default='', blank=True)
    icon = ImageField(upload_to=FilenameGenerator(prefix='treatment_icon'),
                      resize_source_to='source_300', default='', blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    position = models.PositiveIntegerField(blank=True, null=True, default=1)

    def __unicode__(self):
        return self.name
