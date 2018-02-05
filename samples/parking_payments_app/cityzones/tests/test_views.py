from django.test import TestCase
from django.contrib.gis.geos import Polygon, MultiPolygon

from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from .factories import CityParkingZoneFactory
from modules.users.tests.factories import APIUserFactory


class CityParkingZoneListAPIViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = APIUserFactory.create()
        self.client.force_authenticate(user=self.user)
        self.zone = CityParkingZoneFactory.create(
            zone=MultiPolygon(
                Polygon(((0, 0), (0, 1), (1, 0), (0, 0)))
            )
        )

    def get_url(self, **kwargs):
        params = '&'.join(['%s=%s' % (key, kwargs[key]) for key in kwargs])
        return reverse('cityzones:list') + '?' + params

    def test_position_not_in_zone(self):
        response = self.client.get(self.get_url(position="14,0"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_position_in_zone(self):
        response = self.client.get(self.get_url(position="1,0"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_position_directly_in_zone(self):
        response = self.client.get(self.get_url(position="0.5,0.5"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_position_in_two_zones(self):
        CityParkingZoneFactory.create(
            zone=MultiPolygon(
                Polygon(((0, 0), (0, -1), (-1, 0), (0, 0)))
            )
        )
        response = self.client.get(self.get_url(position="0,0"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_no_comma_in_position(self):
        response = self.client.get(self.get_url(position="10"))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['errors'][0]['code'], 1777)

    def test_not_valid_number_in_position(self):
        response = self.client.get(self.get_url(position="1,o"))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['errors'][0]['code'], 1777)

    def test_invalid_accuracy(self):
        response = self.client.get(self.get_url(
            position="1,0", accuracy='corse'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
