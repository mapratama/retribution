from django.db import models
from django.utils import timezone

from model_utils import Choices

from rumahtotok.apps.orders.models import Order


class Promotion(models.Model):
    code = models.CharField(max_length=20, unique=True, db_index=True)
    start_date = models.DateField()
    end_date = models.DateField()
    discount_percentage = models.FloatField(blank=True, null=True)
    discount_nominal = models.FloatField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    TYPE = Choices(
        (1, 'one_time', 'One Time'),
        (2, 'unlimited_use', 'Unlimited Use'),
        (3, 'first_time_user', 'First Time User'),
    )
    type = models.PositiveSmallIntegerField(choices=TYPE)
    services = models.ManyToManyField('services.Service', related_name='promotions')

    def __unicode__(self):
        return self.code

    def validate(self, user, service, order_time=None):
        if not self.is_active:
            return (False, 'Promotion code is no longer valid.')

        if self.type == self.TYPE.one_time:
            if user.orders.filter(promotion_code=self.code).exclude(status=Order.STATUS.canceled).exists():
                return (False, "Promo code can only be used once.")

        elif self.type == self.TYPE.first_time_user:
            if user.orders.exclude(status=Order.STATUS.canceled).exists():
                return (False, "Code is only valid for your first booking.")

        order_date = timezone.localtime(order_time or timezone.now()).date()
        if not self.start_date <= order_date <= self.end_date:
            return (False, "This promo code is no longer valid.")

        promoted_services = list(self.services.all())
        if not service in promoted_services:
            return (False, "Promo code is not valid for services you chose.")

        return (True, "")

    def calculate_discount(self, price):
        if self.discount_percentage:
            return price * self.discount_percentage / 100
        else:
            return self.discount_nominal
