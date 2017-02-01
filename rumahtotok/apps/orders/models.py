from datetime import timedelta
from random import randint
from model_utils import Choices
from model_utils.fields import AutoCreatedField
from thumbnails.fields import ImageField

from django.db import models
from django.db.models import Sum, F
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone

from rumahtotok.apps.balance_updates.models import BalanceUpdate
from rumahtotok.apps.balance_updates.utils import create_balance_update
from rumahtotok.core.utils import (generate_hashids,
                                   prepare_start_date, FilenameGenerator)
from rumahtotok.apps.bookings.models import Booking


class Order(models.Model):
    user = models.ForeignKey('users.User', related_name='orders')
    created = AutoCreatedField()
    service = models.ForeignKey('services.Service', related_name='orders')
    STATUS = Choices(
        (1, 'created', 'Created'),
        (2, 'confirmed', 'Confirmed'),
        (3, 'in_progress', 'In Progress'),
        (4, 'completed', 'Completed'),
        (5, 'canceled', 'Canceled')
    )
    status = models.PositiveSmallIntegerField(choices=STATUS, default=STATUS.created)
    code = models.CharField(max_length=12, unique=True,
                            db_index=True, blank=True, null=True, default=None)
    promotion_code = models.CharField(max_length=24, blank=True, null=True, default='')
    price = models.FloatField(validators=[MinValueValidator(0)], blank=True, null=True)
    unique_price = models.FloatField(validators=[MinValueValidator(0)], blank=True, null=True)
    discount = models.FloatField(validators=[MinValueValidator(0)], blank=True, default=0)
    completed_paid = models.BooleanField(default=False)
    balance_reversed = models.BooleanField(default=False)
    total_payment = models.FloatField(validators=[MinValueValidator(0)], blank=True, default=0)
    total_booking = models.FloatField(validators=[MinValueValidator(0)], blank=True, default=0)
    completed_booking = models.FloatField(validators=[MinValueValidator(0)], blank=True, default=0)

    def __unicode__(self):
        return 'Order-%s' % self.code

    @property
    def duration(self):
        return self.service.time_needed

    @property
    def discounted_price(self):
        return self.price - self.discount

    @property
    def remaining_payment(self):
        return self.discounted_price - self.total_payment

    def calculate_total_booking(self):
        self.total_booking = self.bookings.exclude(status=Booking.STATUS.canceled).count()
        self.save(update_fields=['total_booking'])

        return self.total_booking

    def calculate_completed_booking(self):
        self.completed_booking = self.bookings.filter(status=Booking.STATUS.completed).count()
        self.save(update_fields=['completed_booking'])

        return self.completed_booking

    def calculate_total_payment(self):
        payment = self.payments.aggregate(total_payment=Sum(F("value") + F("balance_used")))
        total_payment = payment['total_payment']
        if not total_payment:
            return 0

        self.total_payment = total_payment
        self.save(update_fields=['total_payment'])
        self.update_payment_status()
        return self.total_payment

    def update_payment_status(self):
        if self.total_payment >= self.discounted_price:
            self.completed_paid = True
        else:
            self.completed_paid = False
        self.save(update_fields=['completed_paid'])

        return self.completed_paid

    def update_status(self):
        self.calculate_completed_booking()
        self.calculate_total_booking()

        if self.total_payment == 0 and self.total_booking == 0:
            self.status = self.STATUS.created

        elif self.total_payment == self.discounted_price:
            self.status = self.STATUS.confirmed
        else:
            self.status = self.STATUS.created

        if 0 < self.total_booking <= self.service.max_booking:
            self.status = self.STATUS.in_progress

        if self.completed_booking == self.service.max_booking:
            self.status = self.STATUS.completed

        self.save(update_fields=['status'])
        return self.status

    def get_code(self):
        if self.code:
            return self.code

        self.code = 'R-' + generate_hashids(self.id, length=6)
        self.save()

        return self.code

    def can_canceled(self):
        if self.status in [Order.STATUS.canceled, Order.STATUS.completed]:
            return False

        if self.bookings.filter(status=Booking.STATUS.completed).exists():
            return False

        return True

    def cancel(self, user):
        bookings = self.bookings.exclude(status=Booking.STATUS.completed)

        for booking in bookings:
            booking.cancel()

        if self.can_reverse_payment():
            self.reverse_payment(created_by=user, notes="Auto add from canceled order")

        self.status = Order.STATUS.canceled
        self.save(update_fields=['status'])

        return self

    def can_reverse_payment(self):
        if self.balance_reversed or self.status in [self.STATUS.completed]:
            return False

        return True

    def reverse_payment(self, created_by, notes=None):
        self.calculate_total_booking()
        discounted_price = self.discounted_price
        total_booking = self.total_booking
        price_per_booking = 0

        if total_booking > 0:
            price_per_booking = discounted_price / total_booking

        remaining_balance = self.total_payment - (total_booking * price_per_booking)
        if remaining_balance <= 0:
            return 0

        self.balance_reversed = True
        self.save(update_fields=['balance_reversed'])
        notes = notes or "Auto add by reverse balance from order"

        create_balance_update(
            user=self.user, value=remaining_balance, order=self,
            type=BalanceUpdate.TYPES.order, created_by=created_by,
            notes=notes)

        return remaining_balance

    def generate_unique_price(self):
        start_date = prepare_start_date(timezone.now().date() - timedelta(days=3))
        first_digit = str(int(self.discounted_price) / 1000)
        last_digit = self.discounted_price % 1000

        if last_digit <= 500:
            start = 101
            max = 499
        else:
            start = 501
            max = 999

        unique_price = int(first_digit + str(randint(start, max)))
        while (PaymentConfirmation.objects.filter(created__gte=start_date,
                                                  value=unique_price).exists()):
            unique_price = first_digit + randint(start, max)

        self.unique_price = unique_price
        self.save(update_fields=['unique_price'])

        return self.unique_price

    def create_workflow(self):
        self.get_code()
        self.generate_unique_price()
        self.calculate_total_booking()
        self.update_status()

        return self.unique_price


class PaymentConfirmation(models.Model):
    order = models.ForeignKey('orders.Order', related_name='payment_confirmations')
    created = AutoCreatedField()
    STATUS = Choices(
        (1, 'new', 'New'),
        (2, 'accepted', 'Accepted'),
        (3, 'rejected', 'Rejected')
    )
    status = models.PositiveSmallIntegerField(choices=STATUS, default=STATUS.new)
    photo_url = models.CharField(max_length=255)
    photo = ImageField(upload_to=FilenameGenerator(prefix='payment_confirmations'),
                       resize_source_to='size_400', default='', blank=True)
    value = models.FloatField(validators=[MinValueValidator(0)], blank=True, null=True)
    correction_by = models.ForeignKey('users.User', related_name='payment_confirmations', blank=True, null=True)
    notes = models.TextField(default='', blank=True)

    def __unicode__(self):
        return 'Order-%s' % self.order.code
