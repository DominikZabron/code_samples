# -*- coding: utf-8 -*-
import datetime
import json
from uuid import uuid4

from django.test import override_settings
from django.utils import timezone
from mock import Mock, patch
from rest_framework import status

from modules.core.tests import APITestCase
from modules.transactions.tests.factories import TransactionFactory
from modules.users.tests.factories import PatientFactory

from .factories import TokenFactory

ACCESS_TOKEN = str(uuid4())
REFRESH_TOKEN = str(uuid4())

PAYU_AUTH_RESPONSE = {
    "access_token": ACCESS_TOKEN,
    "token_type": "bearer",
    "refresh_token": REFRESH_TOKEN,
    "expires_in": 43199,
    "grant_type": "trusted_merchant"
}


class TokenViewAPITestCase(APITestCase):
    def setUp(self):
        self.url = '/paymentprovider/accesstoken'
        self.patient = PatientFactory.create(
            email='patient@email.com', email_verified=True)
        self.assertTrue(self.client.force_login(self.patient))
        super(TokenViewAPITestCase, self).setUp()

    @override_settings(PAYU_CLIENT_ID=1, PAYU_CLIENT_SECRET=1)
    @patch('requests.post')
    def test_success_create_new_token(self, mock_post):
        mock_post.side_effect = mock_response = Mock()
        mock_response.return_value.status_code = 200
        mock_response.return_value.text = json.dumps(PAYU_AUTH_RESPONSE)
        response = self.client.get(self.url)
        self.assertEqual(mock_post.call_count, 1)
        self.assertEqual(mock_response.call_count, 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['access_token'], ACCESS_TOKEN)

    @patch('requests.post')
    def test_success_refresh_token(self, mock_post):
        token = TokenFactory.create(
            patient=self.patient,
            refresh_token=REFRESH_TOKEN,
            expires_in=timezone.now())
        mock_post.side_effect = mock_response = Mock()
        mock_response.return_value.status_code = 200
        mock_response.return_value.text = json.dumps(PAYU_AUTH_RESPONSE)
        self.assertNotEqual(token.access_token, ACCESS_TOKEN)
        response = self.client.get(self.url)
        self.assertEqual(mock_post.call_count, 1)
        self.assertEqual(mock_response.call_count, 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['access_token'], ACCESS_TOKEN)

    def test_success_valid_token(self):
        token = TokenFactory.create(
            patient=self.patient,
            expires_in=timezone.now() + datetime.timedelta(days=1)
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['access_token'], str(token.access_token))


class PaymentStatusAPITestCase(APITestCase):
    def setUp(self):
        self.patient = PatientFactory.create()
        self.transaction = TransactionFactory.create(patient=self.patient)
        self.url = '/paymentprovider/orderstatus'

        self.ORDER_STATUS_COMPLETED = {
            "order": {
                "orderId": "LDLW5N7MF4140324GUEST000P01",
                "extOrderId": self.transaction.payment_id,
                "orderCreateDate": "2012-12-31T12:00:00",
                "notifyUrl": "http://tempuri.org/notify",
                "customerIp": "127.0.0.1",
                "merchantPosId": "{POS ID (pos_id)}",
                "description": "My order description",
                "currencyCode": "PLN",
                "totalAmount": "200",
                "buyer": {
                    "email": "john.doe@example.org",
                    "phone": "111111111",
                    "firstName": "John",
                    "lastName": "Doe"
                },
                "products":
                    {
                        "name": "Product 1",
                        "unitPrice": "200",
                        "quantity": "1"
                },
                "status": "COMPLETED"
            }
        }

        self.ORDER_STATUS_CANCELED = {
            "order": {
                "orderId": "LDLW5N7MF4140324GUEST000P01",
                "extOrderId": self.transaction.payment_id,
                "orderCreateDate": "2012-12-31T12:00:00",
                "notifyUrl": "http://tempuri.org/notify",
                "customerIp": "127.0.0.1",
                "merchantPosId": "{POS ID (pos_id)}",
                "description": "My order description",
                "currencyCode": "PLN",
                "totalAmount": "200",
                "products": {
                    "name": "Product 1",
                    "unitPrice": "200",
                    "quantity": "1"
                },
                "status": "CANCELED"
            }
        }

        self.ORDER_STATUS_PENDING = {
            "order": {
                "extOrderId": self.transaction.payment_id,
                "status": "PENDING"
            }
        }

    def test_success_confirmed(self):
        currency_before = self.patient.currency_balance

        response = self.client.post(self.url, self.ORDER_STATUS_COMPLETED)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.payment_status, 'confirmed')

        self.patient.refresh_from_db()
        self.assertEqual(self.patient.currency_balance,
                         currency_before + self.transaction.amount)

    def test_success_canceled(self):
        response = self.client.post(self.url, self.ORDER_STATUS_CANCELED)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.payment_status, 'canceled')

    def test_fail_no_payload(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_fail_wrong_id(self):
        ORDER_STATUS_CANCELED = {
            "order": {
                "extOrderId": 'qwer789',
                "status": "CANCELED"
            }
        }
        response = self.client.post(self.url, ORDER_STATUS_CANCELED)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_success_pending_before_completed(self):
        response = self.client.post(self.url, self.ORDER_STATUS_PENDING)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.payment_status, 'new')

        response = self.client.post(self.url, self.ORDER_STATUS_COMPLETED)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.payment_status, 'confirmed')

    def test_success_completed_before_pending(self):
        response = self.client.post(self.url, self.ORDER_STATUS_COMPLETED)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.payment_status, 'confirmed')

        response = self.client.post(self.url, self.ORDER_STATUS_PENDING)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.payment_status, 'confirmed')

    def test_success_pending_before_canceled(self):
        response = self.client.post(self.url, self.ORDER_STATUS_PENDING)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.payment_status, 'new')

        response = self.client.post(self.url, self.ORDER_STATUS_CANCELED)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.payment_status, 'canceled')

    def test_success_canceled_before_pending(self):
        response = self.client.post(self.url, self.ORDER_STATUS_CANCELED)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.payment_status, 'canceled')

        response = self.client.post(self.url, self.ORDER_STATUS_PENDING)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.payment_status, 'canceled')
