from django.db import models
from thumbnails.fields import ImageField

from rumahtotok.core.utils import FilenameGenerator


class Therapist(models.Model):
    user = models.OneToOneField('users.User')
    photo = ImageField(
        upload_to=FilenameGenerator(prefix='therapist_photos'),
        resize_source_to='source_300',
        blank=True, help_text='Image must be 800x800 in dimension')
    store = models.ForeignKey('stores.Store', related_name='therapists')
    max_booking = models.PositiveSmallIntegerField(default=5)
    is_active = models.BooleanField(default=True)

    def __unicode__(self):
        return "%s" % self.user

    def merge_adjacent_tasks(self, date):
        tasks = list(self.tasks.only_standby(date).order_by('start'))

        if not tasks:
            return

        first_task = tasks.pop(0)
        while tasks:
            second_task = tasks.pop(0)
            if first_task.end >= second_task.start:
                if first_task.end <= second_task.end:
                    first_task.end = second_task.end
                    first_task.save(update_fields=['end'])

                second_task.delete()
            else:
                first_task = second_task
