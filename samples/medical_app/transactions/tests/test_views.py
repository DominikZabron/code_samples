# -*- coding: utf-8 -*-
from rest_framework import status

from modules.core.tests import APITestCase
from modules.transactionpackages.tests.factories import \
    TransactionPackageFactory
from modules.transactions.tests.factories import TransactionFactory
from modules.users.tests.factories import DoctorFactory, PatientFactory


class TransactionViewTestCase(APITestCase):
    def setUp(self):
        self.url = '/transactions'
        self.patient = PatientFactory.create()
        self.assertTrue(self.client.force_login(self.patient))
        super(TransactionViewTestCase, self).setUp()

    def test_unsuccessful_create_transaction_not_exist(self):
        package = TransactionPackageFactory.create()
        payload = {'transaction_package': package.id}
        package.delete()

        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_payload_not_provided(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_successful_create_transaction(self):
        package = TransactionPackageFactory.create()
        payload = {'transaction_package': package.id}

        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 7)

    def test_empty_list(self):
        # pusta lista
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

        # transakcje innego uzytkownika
        patient = PatientFactory.create()
        TransactionFactory.create_batch(20, patient=patient)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_non_empty_list(self):
        TransactionFactory.create_batch(20, patient=self.patient)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 20)


class BalanceViewTestCase(APITestCase):
    def setUp(self):
        self.url = '/transactions/balance'
        self.patient = PatientFactory.create()
        self.assertTrue(self.client.force_login(self.patient))
        super(BalanceViewTestCase, self).setUp()

    def test_balance(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class TransactionDetailViewTestCase(APITestCase):
    def setUp(self):
        self.url = '/transactions/{0}'
        self.patient = PatientFactory.create()
        self.assertTrue(self.client.force_login(self.patient))
        self.doctor = DoctorFactory.create()

    def test_invalid_transaction_id(self):
        transaction = TransactionFactory.create()
        transaction.delete()

        response = self.client.get(self.url.format(transaction.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_transaction_patient(self):
        transaction = TransactionFactory.create(patient=self.patient)

        response = self.client.get(self.url.format(transaction.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 7)

    def test_invalid_transaction_patient(self):
        # Sprawdzamy transakcje nalezaca do innego pacjenta
        patient = PatientFactory.create()
        transaction = TransactionFactory.create(patient=patient)

        response = self.client.get(self.url.format(transaction.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_transaction_doctor(self):
        self.assertTrue(self.client.force_login(self.doctor))
        patient = PatientFactory(doctor=self.doctor)
        transaction = TransactionFactory.create(patient=patient)

        response = self.client.get(self.url.format(transaction.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 8)

    def test_invalid_transaction_doctor(self):
        # Brak mozliwosci sprawdzenia transakcji pacjenta innego doktora
        self.assertTrue(self.client.force_login(self.doctor))
        doctor = DoctorFactory.create()
        patient = PatientFactory(doctor=doctor)
        transaction = TransactionFactory.create(patient=patient)

        response = self.client.get(self.url.format(transaction.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
