from django.test import TestCase
from rest_framework.test import APIRequestFactory, APIClient

from rest_framework.reverse import reverse
from modules.users.tests.factories import APIUserFactory
from modules.vehicles.tests.factories import VehicleFactory
from .factories import ParkboxFactory


class BeaconRetrieveAPIViewTestCase(TestCase):

    def setUp(self):
        self.user = APIUserFactory.create()
        self.client = APIClient()
        self.factory = APIRequestFactory()
        self.client.force_authenticate(user=self.user)
        self.parkbox = ParkboxFactory.create()
        self.free_parkbox = ParkboxFactory.create()
        self.vehicle = VehicleFactory.create(parkbox=self.parkbox)

    def get_url(self, **kwargs):
        params = '&'.join(['%s=%s' % (key, kwargs[key]) for key in kwargs])
        return reverse('beacons:get') + '?' + params

    def test_retrieve_parkbox(self):
        response = self.client.get(
            self.get_url(uuid=self.free_parkbox.uuid))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['parkbox_id'], str(self.free_parkbox.id))

    def test_retrieve_parkbox_detail(self):
        response = self.client.get(
            self.get_url(
                uuid=self.free_parkbox.uuid,
                major=self.free_parkbox.major,
                minor=self.free_parkbox.minor,
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['parkbox_id'], str(self.free_parkbox.id))

    def test_retrieve_parkbox_registered_other_car(self):
        parkbox = ParkboxFactory.create()
        VehicleFactory.create(parkbox=parkbox, user=self.user)
        response = self.client.get(self.get_url(uuid=parkbox.uuid))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['errors'][0]['code'], 7011)

    def test_retrieve_parkbox_owned_other_user(self):
        response = self.client.get(self.get_url(uuid=self.parkbox.uuid))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['errors'][0]['code'], 7012)

    def test_retrieve_parkbox_major_and_minor_is_required(self):
        pbox = ParkboxFactory(uuid=self.free_parkbox.uuid)
        self.assertNotEqual(pbox.major, self.free_parkbox.major)

        response = self.client.get(
            self.get_url(uuid=self.free_parkbox.uuid))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['errors'][0]['code'], 7013)

        response = self.client.get(
            self.get_url(
                uuid=self.free_parkbox.uuid,
                major=self.free_parkbox.major,
                minor=self.free_parkbox.minor,
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['parkbox_id'], str(self.free_parkbox.id))

    def test_retrieve_parkbox_not_exist(self):
        # We use id instead of uuid
        response = self.client.get(self.get_url(uuid=self.free_parkbox.id))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['errors'][0]['code'], 7014)
