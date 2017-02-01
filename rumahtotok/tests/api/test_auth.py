import json
import urllib

from django.core.urlresolvers import reverse
from django.utils import timezone

from rumahtotok.apps.users.models import User, Confirmation
from rumahtotok.tests import RumahTotokTestCase

from datetime import timedelta


class ViewTest(RumahTotokTestCase):
    fixtures = ['users.json']

    def test_register(self):
        data = {
            "token": self.token,
            "email": "test@gmail.com",
            "name": "aku imam",
            "password": "PASSWORD",
            "mobile_number": "087877543295",
            "gender": 1,
            "birthday": "1990-31-12"
        }

        # Invalid Birthday
        response = self.client.post(reverse('api:auth:register'),
                                    json.dumps(data), **self.headers)
        self.assertEqual(response.status_code, 400)

        # mobile number already in use
        data["birthday"] = "1990-12-1"
        response = self.client.post(reverse('api:auth:register'),
                                    json.dumps(data), **self.headers)
        self.assertEqual(response.status_code, 400)

        # Update data, If user is created from backoffice
        user = User.objects.get(username="+6287877543295")
        user.created_from = User.CREATED_FROM.backoffice
        user.save()

        data["birthday"] = "1990-12-1"
        response = self.client.post(reverse('api:auth:register'),
                                    json.dumps(data), **self.headers)
        self.assertEqual(response.status_code, 200)

        user = User.objects.get(username="+6287877543295")
        self.assertEqual(user.name, "Aku Imam")
        self.assertEqual(user.type, User.TYPE.customer)

    def test_login(self):
        data = {
            "username": '+6287877543295',
            "password": 'imam',
            "gcm_key": "12345",
            "token": self.token
        }
        response = self.client.post(reverse('api:auth:login'),
                                    json.dumps(data), **self.headers)

        response_json = json.loads(response.content)
        self.assertEqual(response_json['user']['id'], 1)
        self.assertNotEqual(response_json['session_key'], None)
        self.assertEqual(response.status_code, 200)

        # logout
        user = User.objects.get(username='+6287877543295')
        self.assertEqual(user.gcm_key, "12345")

        data = {
            "token": self.token,
            "session_key": response_json['session_key']
        }
        response = self.client.post(reverse('api:auth:logout'),
                                    json.dumps(data), **self.headers)

        user = User.objects.get(username='+6287877543295')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(user.gcm_key, '')

        # try to get product list via API
        # should return error, because session_key has been deleted in server
        url = reverse('api:orders:index')
        url = url + '?' + urllib.urlencode(data)
        response = self.client.get(url, **self.headers)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(json.loads(response.content)['detail'], 'Invalid session id')

        # # login with invalid username
        data['username'] = 'rudi'
        response = self.client.post(reverse('api:auth:login'),
                                    json.dumps(data), **self.headers)
        self.assertEqual(response.status_code, 400)

        # login with invalid username
        data['username'] = '+62087877543295'
        data['token'] = '1nv4l1d70k3n'
        response = self.client.post(reverse('api:auth:login'),
                                    json.dumps(data), **self.headers)
        self.assertEqual(response.status_code, 403)

    def test_get_confirmation_code(self):
        Confirmation.objects.all().delete()

        data = {
            "token": self.token,
            "mobile_number": "087877543298",
        }

        # Mobile number not found
        response = self.client.post(reverse('api:auth:get_confirmation_code'),
                                    json.dumps(data), **self.headers)
        self.assertEqual(response.status_code, 400)

        # mobile number already in use
        data["mobile_number"] = "087877543295"
        response = self.client.post(reverse('api:auth:get_confirmation_code'),
                                    json.dumps(data), **self.headers)
        self.assertEqual(response.status_code, 200)

        # shouldn't return error
        Confirmation.objects.get(mobile_number="+6287877543295")

    def test_reset_password(self):
        Confirmation.objects.create(
            mobile_number="+6287877543295", code="1234",
            valid_until=timezone.now() + timedelta(days=10))

        Confirmation.objects.create(
            mobile_number="+6287877543295", code="1235",
            valid_until=timezone.now() + timedelta(days=10))

        data = {
            "token": self.token,
            "mobile_number": "087877543295",
            "code": "9367",
            "password": "imamoke"
        }

        # InvalidCode
        response = self.client.post(reverse('api:auth:reset_password'),
                                    json.dumps(data), **self.headers)
        self.assertEqual(response.status_code, 400)

        # All Confirmation by this number shuld be deleted
        data["code"] = "1235"
        response = self.client.post(reverse('api:auth:reset_password'),
                                    json.dumps(data), **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Confirmation.objects.all().count(), 0)

        # User can login with new password
        data = {
            "username": '087877543295',
            "password": 'imamoke',
            "token": self.token
        }
        response = self.client.post(reverse('api:auth:login'),
                                    json.dumps(data), **self.headers)
        self.assertEqual(response.status_code, 200)
