from django.db import models

from model_utils import Choices
from model_utils.fields import AutoCreatedField


class BalanceUpdate(models.Model):
    user = models.ForeignKey('users.User', related_name='balance_updates')
    order = models.ForeignKey('orders.Order', related_name='balances',
                              blank=True, null=True)

    TYPES = Choices(
        (1, 'order', 'Order'),
        (2, 'manual', 'Manual'),
        (3, 'referral', 'Referral'),
    )
    type = models.PositiveSmallIntegerField(choices=TYPES)

    STATUS = Choices(
        (1, 'created', 'Created'),
        (2, 'canceled', 'Canceled'),
    )
    status = models.PositiveSmallIntegerField(choices=STATUS, default=STATUS.created)
    value = models.IntegerField()
    created = AutoCreatedField()
    created_by = models.ForeignKey('users.User', related_name='created_balances')
    canceled_by = models.ForeignKey('users.User', default=None, blank=True, null=True,
                                    related_name='canceled_balances')
    notes = models.TextField(default='', blank=True)

    def __unicode__(self):
        return "%s's balance" % (self.user)
