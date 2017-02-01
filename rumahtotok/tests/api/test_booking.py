import json

from django.core.urlresolvers import reverse
from django.utils import timezone

from rumahtotok.apps.bookings.models import Booking
from rumahtotok.apps.orders.models import Order
from rumahtotok.apps.stores.models import Store
from rumahtotok.apps.users.models import User

from rumahtotok.tests import RumahTotokTestCase

from datetime import timedelta


class ViewTest(RumahTotokTestCase):
    fixtures = ['users.json', "treatments.json"]

    def setUp(self):
        self.user = User.objects.get(username='+6287877543295')
        self.session_key = self.get_session_key('+6287877543295', 'imam')
        self.store = Store.objects.create(name="Store", max_male_booking=1)
        self.now = timezone.localtime(timezone.now())

    def test_booking_preview(self):
        data = {
            "token": self.token,
            "session_key": self.session_key,
            "service": 21,
            "store": self.store.id,
            "date": self.now.strftime("%Y-%m-%d"),
        }

        response = self.client.post(reverse('api:bookings:preview'),
                                    json.dumps(data), **self.headers)
        self.assertEqual(response.status_code, 200)

        # case future booking time
        data["date"] = "2000-01-02"
        response = self.client.post(reverse('api:bookings:preview'),
                                    json.dumps(data), **self.headers)
        self.assertEqual(response.status_code, 400)

        # case date > 30 days from now
        data["date"] = (self.now + timedelta(days=31)).strftime("%Y-%m-%d")
        response = self.client.post(reverse('api:bookings:preview'),
                                    json.dumps(data), **self.headers)
        self.assertEqual(response.status_code, 400)

        # Store has been reached maximal booking
        order = Order.objects.create(user=self.user, service_id=22)
        order.bookings.create(store=self.store, created_by=self.user,
                              date=self.now.strftime("%Y-%m-%d"))

        data["date"] = self.now.strftime("%Y-%m-%d")
        response = self.client.post(reverse('api:bookings:preview'),
                                    json.dumps(data), **self.headers)
        self.assertEqual(response.status_code, 400)

    def test_booking_creation(self):
        data = {
            "token": self.token,
            "session_key": self.session_key,
            "service": 21,
            "store": self.store.id,
            "date": self.now.strftime("%Y-%m-%d"),
        }

        # Order Required
        response = self.client.post(reverse('api:bookings:create'),
                                    json.dumps(data), **self.headers)
        self.assertEqual(response.status_code, 400)
        order = Order.objects.create(user=self.user, service_id=21, code="1233",
                                     price=100000, discount=10000)

        # not paid order will available create booking for once
        data["order"] = order.id
        response = self.client.post(reverse('api:bookings:create'),
                                    json.dumps(data), **self.headers)
        self.assertEqual(response.status_code, 200)

        # Try to booking in a same date in one order
        order.completed_paid = True
        order.save()
        response = self.client.post(reverse('api:bookings:create'),
                                    json.dumps(data), **self.headers)
        self.assertEqual(response.status_code, 400)

        # Case booking reach maximum number
        order.calculate_total_booking()
        data["date"] = (self.now + timedelta(days=1)).strftime("%Y-%m-%d")
        response = self.client.post(reverse('api:bookings:create'),
                                    json.dumps(data), **self.headers)
        self.assertEqual(response.status_code, 400)

        # Case not paid booking try to add other booking
        order.completed_paid = False
        order.save()
        data["date"] = (self.now + timedelta(days=1)).strftime("%Y-%m-%d")
        response = self.client.post(reverse('api:bookings:create'),
                                    json.dumps(data), **self.headers)
        self.assertEqual(response.status_code, 400)

        # .......................... TEST BOOKING CANCEL ......................

        booking = Booking.objects.last()
        booking.status = Booking.STATUS.completed
        booking.save()

        # Case booking complete
        data = {
            "token": self.token,
            "session_key": self.session_key,
            "booking": booking.id,
        }

        # Case booking complete
        response = self.client.post(reverse('api:bookings:cancel'),
                                    json.dumps(data), **self.headers)
        self.assertEqual(response.status_code, 400)

        # Case booking cancel
        booking.status = Booking.STATUS.canceled
        booking.save()
        response = self.client.post(reverse('api:bookings:cancel'),
                                    json.dumps(data), **self.headers)
        self.assertEqual(response.status_code, 400)

        booking.status = Booking.STATUS.assigned
        booking.save()

        order.status = Order.STATUS.completed
        order.save()

        response = self.client.post(reverse('api:bookings:cancel'),
                                    json.dumps(data), **self.headers)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(booking.order.total_booking, 0)
        self.assertEqual(booking.order.completed_booking, 0)

        order = Order.objects.last()
        self.assertEqual(order.status, Order.STATUS.created)

    def test_booking_review(self):
        order = Order.objects.create(user=self.user, service_id=21, code="1233",
                                     price=100000, discount=10000)
        booking = order.bookings.create(store=self.store,
                                        date=self.now.strftime("%Y-%m-%d"),
                                        created_by=self.user,
                                        status=Booking.STATUS.completed)
        data = {
            "token": self.token,
            "session_key": self.session_key,
            "booking": booking.id,
            "rating": 4,
            "review": "Good"
        }

        response = self.client.post(reverse('api:bookings:review'),
                                    json.dumps(data), **self.headers)
        self.assertEqual(response.status_code, 200)

        booking = Booking.objects.last()
        self.assertEqual(booking.rating, 4)
        self.assertEqual(booking.review, "Good")

        # Case booking has been reviewed
        response = self.client.post(reverse('api:bookings:review'),
                                    json.dumps(data), **self.headers)
        self.assertEqual(response.status_code, 400)

    def test_booking_edit(self):
        order = Order.objects.create(user=self.user, service_id=21, code="1233",
                                     price=100000, discount=10000)
        booking = order.bookings.create(store=self.store,
                                        date=self.now.strftime("%Y-%m-%d"),
                                        created_by=self.user,
                                        status=Booking.STATUS.completed)
        data = {
            "token": self.token,
            "session_key": self.session_key,
            "booking": booking.id,
            "store": self.store.id,
            "date": self.now.strftime("%Y-%m-%d"),
        }

        # No Changes Detected
        response = self.client.post(reverse('api:bookings:edit'),
                                    json.dumps(data), **self.headers)
        self.assertEqual(response.status_code, 400)

        # Specify future or today
        data["date"] = (self.now - timedelta(days=1)).strftime("%Y-%m-%d")
        response = self.client.post(reverse('api:bookings:edit'),
                                    json.dumps(data), **self.headers)
        self.assertEqual(response.status_code, 400)

        # Valid Form
        data["date"] = (self.now + timedelta(days=1)).strftime("%Y-%m-%d")
        response = self.client.post(reverse('api:bookings:edit'),
                                    json.dumps(data), **self.headers)
        self.assertEqual(response.status_code, 200)
        booking = Booking.objects.last()
        self.assertEqual(booking.date, (self.now + timedelta(days=1)).date())
