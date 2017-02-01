from django.core.validators import MinValueValidator
from django.db import models


class Service(models.Model):
    treatment = models.ForeignKey('treatments.Treatment', related_name='services')
    name = models.CharField('Name', max_length=255)
    time_needed = models.PositiveSmallIntegerField(default=0)
    price = models.FloatField(validators=[MinValueValidator(0)])
    discounted_price = models.FloatField(validators=[MinValueValidator(0)], blank=True, null=True)
    number_of_visit = models.PositiveSmallIntegerField('Number Of Visit', default=1)
    number_of_people = models.PositiveSmallIntegerField('Number Of People', default=1)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __unicode__(self):
        return "%s  :  %s" % (self.treatment.name, self.name)

    @property
    def max_booking(self):
        return self.number_of_people * self.number_of_visit

    @property
    def correct_price(self):
        return self.discounted_price or self.price

    class Meta:
        unique_together = (('treatment', 'name'), )
