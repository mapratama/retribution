from __future__ import unicode_literals

from django.utils import timezone
from django.contrib.auth.models import (AbstractBaseUser, PermissionsMixin,
                                        UserManager)
from django.db import models
from model_utils import Choices


from retribution.core.validators import validate_mobile_number


class CustomUserManager(UserManager):

    def create_user(self, username, password, **extra_fields):
        now = timezone.now()
        user = self.model(username=username,
                          is_active=True, is_superuser=False,
                          last_login=now, date_joined=now, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, username, password, **extra_fields):
        user = self.create_user(username=username, type=User.TYPE.employee,
                                password=password, **extra_fields)
        user.is_staff = True
        user.is_active = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, blank=True, unique=True,
                                db_index=True)
    name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(
        'email address', null=True, blank=True, max_length=254, db_index=True, unique=True,
        default=None)
    mobile_number = models.CharField(
        'Mobile Number', max_length=30, unique=True, null=True,
        db_index=True, blank=True, validators=[validate_mobile_number])
    is_active = models.BooleanField('active', default=True)
    is_staff = models.BooleanField('staff status', default=False)
    date_joined = models.DateTimeField('date joined', default=timezone.now)

    objects = CustomUserManager()
    USERNAME_FIELD = 'username'

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __unicode__(self):
        return self.name or self.username or self.email or 'User #%d' % (self.id)

    def get_short_name(self):
        return self.name or self.username or self.email


class Employee(models.Model):
    user = models.ForeignKey('users.User', related_name='employees')
    destinations = models.ManyToManyField('destinations.Destination', blank=True,
                                          related_name='employees')

    def __unicode__(self):
        return "%s" % self.user

    @property
    def get_total_active_destinations(self):
        return self.destinations.all().count()
