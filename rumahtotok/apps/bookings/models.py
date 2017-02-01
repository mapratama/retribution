from django.db import models

from model_utils import Choices
from model_utils.fields import AutoCreatedField

from rumahtotok.core.utils import generate_hashids


class Booking(models.Model):
    order = models.ForeignKey('orders.Order', related_name='bookings')
    store = models.ForeignKey('stores.Store', related_name='bookings')
    therapist = models.ForeignKey('therapists.Therapist', related_name='bookings',
                                  blank=True, null=True)
    date = models.DateField()
    STATUS = Choices(
        (1, 'new', 'New'),
        (2, 'assigned', 'Assigned'),
        (3, 'completed', 'Completed'),
        (4, 'canceled', 'Canceled'),
    )
    status = models.PositiveSmallIntegerField(choices=STATUS, default=STATUS.new)
    created = AutoCreatedField()
    duration = models.PositiveSmallIntegerField(default=0)  # In minutes
    code = models.CharField(max_length=8, db_index=True, blank=True)
    notes = models.TextField(default='', blank=True)
    RATING = Choices(
        (1, 'one', '1 - Bad'),
        (2, 'two', '2'),
        (3, 'three', '3 - Average'),
        (4, 'four', '4'),
        (5, 'five', '5 - Best'),
    )
    rating = models.PositiveSmallIntegerField(choices=RATING, blank=True, null=True)
    review = models.TextField(default='', blank=True)
    created_by = models.ForeignKey('users.User', related_name='bookings')
    PLATFORM = Choices(
        (1, 'api', 'API (Mobile)'),
        (2, 'backoffice', 'Backoffice'),
    )
    platform = models.PositiveSmallIntegerField(choices=PLATFORM, blank=True, null=True)

    def __unicode__(self):
        return 'Booking #%s' % (self.code)

    def can_reprocessed(self):
        if self.status in [Booking.STATUS.canceled, Booking.STATUS.completed]:
            return False
        return True

    def cancel(self):
        self.status = self.STATUS.canceled
        self.save(update_fields=['status'])

        self.order.calculate_total_booking()
        self.order.calculate_completed_booking()
        self.order.update_status()

    def set_completed(self):
        self.status = Booking.STATUS.completed
        self.save(update_fields=['status'])

        self.order.calculate_total_booking()
        self.order.calculate_completed_booking()
        self.order.update_status()

    def get_code(self):
        if self.code:
            return self.code

        self.code = 'B-' + generate_hashids(self.id, length=5)
        self.save()

        return self.code

    def create_workflow(self):
        self.get_code()
        self.order.calculate_total_booking()
        self.order.calculate_completed_booking()
        self.order.update_status()
