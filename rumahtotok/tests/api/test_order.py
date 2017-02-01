import json

from django.core.urlresolvers import reverse
from django.utils import timezone

from rumahtotok.apps.orders.models import Order
from rumahtotok.apps.promotions.models import Promotion
from rumahtotok.apps.services.models import Service
from rumahtotok.apps.users.models import User

from rumahtotok.tests import RumahTotokTestCase

from datetime import timedelta


class ViewTest(RumahTotokTestCase):
    fixtures = ['users.json', "treatments.json"]

    def setUp(self):
        self.user = User.objects.get(username='+6287877543295')
        self.session_key = self.get_session_key('+6287877543295', 'imam')

    def test_order_cration(self):
        data = {
            "token": self.token,
            "session_key": self.session_key,
            "service": 21,
        }

        # Order should complete previous payment
        previous_order = Order.objects.create(user=self.user, service_id=22)
        response = self.client.post(reverse('api:orders:create'),
                                    json.dumps(data), **self.headers)
        self.assertEqual(response.status_code, 400)

        # Case order request with invalid promotion code
        previous_order.delete()
        data["promotion_code"] = "PROMO"
        response = self.client.post(reverse('api:orders:create'),
                                    json.dumps(data), **self.headers)
        self.assertEqual(response.status_code, 400)

        # Case InValid Product Promotion
        service = Service.objects.get(id=22)
        promotion = Promotion.objects.create(
            code="PROMO", start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=7),
            discount_percentage=10, type=2
        )
        promotion.services.add(service)
        response = self.client.post(reverse('api:orders:create'),
                                    json.dumps(data), **self.headers)
        self.assertEqual(response.status_code, 400)

        # Case Valid Promo
        data["service"] = 22
        promotion.services.add(service)
        response = self.client.post(reverse('api:orders:create'),
                                    json.dumps(data), **self.headers)
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.content)
        self.assertEqual(response_json["price"], 200000)
        self.assertEqual(response_json["discount"], 20000)
        self.assertEqual(response_json["service"]["id"], 22)
        self.assertEqual(response_json["promotion_code"], "PROMO")
        self.assertNotEqual(response_json["code"], "")
        self.assertNotEqual(response_json["unique_price"], "")

        # User has enough balance
        self.user.orders.all().delete()

        self.user.balance = 500000
        self.user.save()

        data["promotion_code"] = ""
        response = self.client.post(reverse('api:orders:create'),
                                    json.dumps(data), **self.headers)
        response_json = json.loads(response.content)

        user = User.objects.get(username='+6287877543295')
        self.assertEqual(user.balance, 300000)
        order = Order.objects.get(id=response_json["id"])
        self.assertEqual(order.payments.all().count(), 1)
        self.assertEqual(self.user.balance_updates.last().value, -200000)

    def test_validation_promotion_view(self):
        data = {
            "token": self.token,
            "session_key": self.session_key,
            "service": 21,
            "promotion_code": "PROMO"
        }

        # Case Invalid
        response = self.client.post(reverse('api:orders:validate_promotion'),
                                    json.dumps(data), **self.headers)
        self.assertEqual(response.status_code, 400)

        # Case Valid Promotion
        service = Service.objects.get(id=21)
        promotion = Promotion.objects.create(
            code="PROMO", start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=7),
            discount_percentage=10, type=2
        )
        promotion.services.add(service)

        data["service"] = 21
        promotion.services.add(service)
        response = self.client.post(reverse('api:orders:validate_promotion'),
                                    json.dumps(data), **self.headers)
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.content)
        self.assertEqual(response_json["price"], 100000)
        self.assertEqual(response_json["discount"], 10000)
        self.assertEqual(response_json["amount_to_pay"], 90000)

        # Not enough user balance will not be used
        self.user.balance = 50000
        self.user.save()
        response = self.client.post(reverse('api:orders:validate_promotion'),
                                    json.dumps(data), **self.headers)
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.content)
        self.assertEqual(response_json["amount_to_pay"], 90000)

        # User has enough balance
        self.user.balance = 200000
        self.user.save()
        response = self.client.post(reverse('api:orders:validate_promotion'),
                                    json.dumps(data), **self.headers)
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.content)
        self.assertEqual(response_json["balance_used"], 90000)
        self.assertEqual(response_json["amount_to_pay"], 0)

    #def test_order_cancel(self):
