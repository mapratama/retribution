from django.db import models

from model_utils import Choices
from model_utils.fields import AutoCreatedField


class TaskGenerationLog(models.Model):

    date = models.DateField()
    created = AutoCreatedField()
    STATUS = Choices(
        (1, 'completed', 'Completed'),
        (2, 'failed', 'Failed'),
    )
    status = models.PositiveIntegerField(choices=STATUS)

    def __unicode__(self):
        return '#%s - %s' % (self.id, self.get_status_display())
