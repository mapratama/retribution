from __future__ import unicode_literals

from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import (AbstractBaseUser, PermissionsMixin,
                                        UserManager)
from django.db import models
from model_utils import Choices
from model_utils.fields import AutoCreatedField
from random import randint
from thumbnails.fields import ImageField


from rumahtotok.core.validators import validate_mobile_number
from rumahtotok.core.utils import FilenameGenerator, generate_hashids


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
    GENDER = Choices(
        (1, 'male', 'Male'),
        (2, 'female', 'Female'),
    )
    gender = models.PositiveSmallIntegerField(choices=GENDER, blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    email = models.EmailField(
        'email address', null=True, blank=True, max_length=254, db_index=True, unique=True,
        default=None)
    mobile_number = models.CharField(
        'Mobile Number', max_length=30, unique=True, null=True,
        db_index=True, blank=True, validators=[validate_mobile_number])
    is_active = models.BooleanField('active', default=True)
    is_staff = models.BooleanField('staff status', default=False)
    date_joined = models.DateTimeField('date joined', default=timezone.now)
    notes = models.TextField(blank=True)
    address = models.TextField(blank=True)
    lat = models.FloatField(blank=True, null=True, default=None)
    long = models.FloatField(blank=True, null=True, default=None)
    referral_code = models.CharField(blank=True, null=True, db_index=True,
                                     unique=True, max_length=10)
    code = models.CharField(blank=True, null=True, db_index=True,
                            unique=True, max_length=10)
    balance = models.FloatField(default=0)
    TYPE = Choices(
        (1, 'employee', 'Employee'),
        (2, 'customer', 'Customer'),
        (3, 'therapist', 'Therapist')
    )
    type = models.PositiveSmallIntegerField(choices=TYPE, default=TYPE.customer)
    CREATED_FROM = Choices(
        (1, 'api', 'API'),
        (2, 'backoffice', 'Backoffice'),
    )
    created_from = models.PositiveSmallIntegerField(choices=CREATED_FROM, default=CREATED_FROM.api)
    photo = ImageField(
        upload_to=FilenameGenerator(prefix='users'),
        resize_source_to='source_300',
        blank=True, help_text='Image must be 300x300 in dimension')
    gcm_key = models.CharField(blank=True, default='', max_length=254)

    objects = CustomUserManager()
    USERNAME_FIELD = 'username'

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __unicode__(self):
        return self.name or self.username or self.email or 'User #%d' % (self.id)

    def get_short_name(self):
        return self.username

    def get_code(self):
        if self.code:
            return self.code

        self.code = 'U-' + generate_hashids(self.id, length=4)
        self.save()

        return self.code

    def has_enough_balance(self, discounted_price):
        if self.balance >= discounted_price:
            return True
        return False


class Confirmation(models.Model):
    mobile_number = models.CharField(max_length=255)
    code = models.CharField(max_length=5)
    is_active = models.BooleanField(default=True)
    valid_until = models.DateTimeField("Valid until")
    created = AutoCreatedField()

    class Meta:
        unique_together = (('mobile_number', 'code'), )

    def __unicode__(self):
        return self.mobile_number

    @classmethod
    def new(cls, number):
        # Valid only for a day, after that we need to clean this up
        valid_until = timezone.now() + timedelta(days=7)

        # Make sure code is unique
        code = "{}{}{}{}{}".format(randint(0, 9), randint(0, 9),
                                   randint(0, 9), randint(0, 9),
                                   randint(0, 9))

        confirmation = cls.objects.create(code=code, mobile_number=number,
                                          valid_until=valid_until)
        return confirmation


class Employee(models.Model):
    user = models.ForeignKey('users.User', related_name='employees')
    stores = models.ManyToManyField('stores.Store', blank=True,
                                    related_name='stores')

    def __unicode__(self):
        return "%s" % self.user
