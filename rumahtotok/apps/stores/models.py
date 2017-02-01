from django.db import models

from thumbnails.fields import ImageField

from rumahtotok.core.utils import FilenameGenerator
from rumahtotok.apps.users.models import User


class Store(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=255, blank=True)
    BBM_pin = models.CharField(max_length=255, blank=True)
    max_male_booking = models.PositiveSmallIntegerField(default=1)
    max_female_booking = models.PositiveSmallIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    photo = ImageField(upload_to=FilenameGenerator(prefix='store'),
                       resize_source_to='resize_300', default='', blank=True)
    lat = models.FloatField(blank=True, null=True)
    long = models.FloatField(blank=True, null=True)

    def __unicode__(self):
        return self.name

    def available_for_booking(self, user, date):
        gender = user.gender or User.GENDER.female
        number_of_bookings = self.bookings.filter(date=date, order__user__gender=gender).count()

        max_booking = self.max_female_booking
        if gender == User.GENDER.male:
            max_booking = self.max_male_booking

        if number_of_bookings < max_booking:
            return True

        return False
