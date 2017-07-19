import random

from django.db import models

from django.core.validators import MinValueValidator

from model_utils import Choices
from model_utils.fields import AutoCreatedField


class Retribution(models.Model):

    destination = models.ForeignKey('destinations.Destination', related_name='retributions')
    qr_code = models.CharField(max_length=254, db_index=True)
    TYPE = Choices(
        (1, 'local', 'Local'),
        (2, 'mancanegara', 'Mancanegara'),
    )

    type = models.PositiveSmallIntegerField(choices=TYPE, default=TYPE.local)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(0)])

    TRANSPORT = Choices(
        (1, 'motor', 'Motor'),
        (2, 'sedan', 'Sedan'),
        (3, 'mini_bus', 'Mini Bus'),
        (4, 'micro_bus', 'Micro Bus'),
        (5, 'bus', 'Bus'),
    )

    transport = models.PositiveSmallIntegerField(choices=TRANSPORT, blank=True, null=True)
    transport_id = models.CharField('Nomor Kendaraan', max_length=50, blank=True, null=True)
    mobile_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(max_length=20, blank=True, null=True)
    has_submitted = models.BooleanField(default=False)
    price = models.FloatField(validators=[MinValueValidator(0)])

    created = AutoCreatedField()
    created_by = models.ForeignKey('users.User', related_name='retributions')

    def __unicode__(self):
        return self.qr_code

    def save(self, *args, **kwargs):
        if not self.qr_code:
            self.qr_code = ''.join(random.choice('12346789ACFHJKLTUXZ')
                                   for i in range(12))
        retribution = super(Retribution, self).save(*args, **kwargs)
        return retribution

    @property
    def generate_barcode(self):
        transport = ''
        if self.transport:
            transport = 'with %s ' % self.get_transport_display()

        info = str("%s for %s people (%s Tourism) %sat %s" %
                   (self.destination, self.quantity, self.get_type_display(),
                    transport, self.created.strftime("%d %B %Y, %H:%M")))
        info = info.replace(" ", "+")

        data = "https://barcode.tec-it.com/barcode.ashx?translate-esc=off&data="
        data += "%s&code=MobileQRCode&unit=Fit&dpi=96&imagetype=Gif&rotation=0" % info
        data += "&color=000000&bgcolor=FFFFFF&qunit=Mm&quiet=0&eclevel=L' alt='Barcode Generator TEC-IT'"

        return data
