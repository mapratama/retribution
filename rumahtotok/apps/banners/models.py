from django.db import models

from thumbnails.fields import ImageField
from rumahtotok.core.utils import FilenameGenerator


class Banner(models.Model):
    image1 = ImageField(upload_to=FilenameGenerator(prefix='banner'),
                        default='', blank=True)
    image2 = ImageField(upload_to=FilenameGenerator(prefix='banner'),
                        default='', blank=True)
    image3 = ImageField(upload_to=FilenameGenerator(prefix='banner'),
                        default='', blank=True)
    image4 = ImageField(upload_to=FilenameGenerator(prefix='banner'),
                        default='', blank=True)

    def __unicode__(self):
        return "%s" % self.id
