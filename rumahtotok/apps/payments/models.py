from django.core.validators import MinValueValidator
from django.db import models

from model_utils.fields import AutoCreatedField
from model_utils import Choices

from rumahtotok.apps.balance_updates.utils import create_balance_update
from rumahtotok.apps.balance_updates.models import BalanceUpdate


class Payment(models.Model):
    order = models.ForeignKey('orders.Order', related_name='payments')
    balance_used = models.FloatField(validators=[MinValueValidator(0)])
    value = models.FloatField(validators=[MinValueValidator(0)])
    code = models.CharField(max_length=10, db_index=True, default=None)
    notes = models.TextField(default='', blank=True)
    created_by = models.ForeignKey('users.User', related_name='payments', blank=True, null=True)
    METHOD = Choices(
        (1, 'cash', 'Cash'),
        (2, 'transfer', 'Transfer'),
        (3, 'balance', 'Balance'),
        (4, 'cash&balance', 'Cash and Balance')
    )
    method = models.PositiveSmallIntegerField(choices=METHOD, default=METHOD.cash)
    time = AutoCreatedField()

    def __unicode__(self):
        return self.code

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.order.code + self.time.strftime("%m%d")
        payment = super(Payment, self).save(*args, **kwargs)
        return payment

    def update_balance(self):
        if self.balance_used:
            create_balance_update(
                user=self.order.user, value=-self.balance_used, order=self.order,
                type=BalanceUpdate.TYPES.order, created_by=self.created_by,
                notes="Auto reduce by payemnt order"
            )
        return self.balance_used
