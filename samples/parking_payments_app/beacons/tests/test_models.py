from django.test import TestCase

from modules.vehicles.tests.factories import VehicleFactory
from .factories import ParkboxFactory
from ..models import ParkboxHistory


class ParkboxStatesTestCase(TestCase):
    def setUp(self):
        self.parkbox = ParkboxFactory.create()
        self.vehicle = VehicleFactory.create(parkbox=self.parkbox)

    def test_associate_free(self):
        self.assertEqual(self.parkbox.state, 'free')
        self.parkbox.associate()
        self.parkbox.save()
        self.parkbox.refresh_from_db()
        self.assertEqual(self.parkbox.state, 'associated')
        hist_entry = ParkboxHistory.objects.filter(
            parkbox=self.parkbox).latest('created_at')
        self.assertEqual(hist_entry.state, 'associated')

    def test_associate_no_vehicle(self):
        parkbox = ParkboxFactory.create()
        self.assertEqual(parkbox.state, 'free')
        self.parkbox.associate()
        self.parkbox.save()
        self.parkbox.refresh_from_db()
        self.assertEqual(parkbox.state, 'free')
        hist_entry = ParkboxHistory.objects.filter(
            parkbox=parkbox).latest('created_at')
        self.assertEqual(hist_entry.state, 'free')

    def test_associate_restored(self):
        parkbox = ParkboxFactory.create(state='restored')
        VehicleFactory.create(parkbox=parkbox)
        self.assertEqual(parkbox.state, 'restored')
        parkbox.associate()
        parkbox.save()
        parkbox.refresh_from_db()
        self.assertEqual(parkbox.state, 'associated')
        hist_entry = ParkboxHistory.objects.filter(
            parkbox=parkbox).latest('created_at')
        self.assertEqual(hist_entry.state, 'associated')

    def test_disassociate(self):
        parkbox = ParkboxFactory.create(state='associated')
        vehicle = VehicleFactory.create(parkbox=parkbox)
        self.assertEqual(parkbox.state, 'associated')
        self.assertEqual(vehicle.parkbox, parkbox)
        parkbox.disassociate()
        parkbox.save()
        parkbox.refresh_from_db()
        self.assertEqual(parkbox.state, 'disassociated')
        hist_entry = ParkboxHistory.objects.filter(
            parkbox=parkbox).latest('created_at')
        self.assertEqual(hist_entry.state, 'disassociated')

    def test_restore_disassociated(self):
        parkbox = ParkboxFactory.create(state='disassociated')
        self.assertEqual(parkbox.state, 'disassociated')
        parkbox.restore()
        parkbox.save()
        parkbox.refresh_from_db()
        self.assertEqual(parkbox.state, 'restored')
        hist_entry = ParkboxHistory.objects.filter(
            parkbox=parkbox).latest('created_at')
        self.assertEqual(hist_entry.state, 'restored')

    def test_restore_removed(self):
        parkbox = ParkboxFactory.create(state='removed')
        self.assertEqual(parkbox.state, 'removed')
        parkbox.restore()
        parkbox.save()
        parkbox.refresh_from_db()
        self.assertEqual(parkbox.state, 'restored')
        hist_entry = ParkboxHistory.objects.filter(
            parkbox=parkbox).latest('created_at')
        self.assertEqual(hist_entry.state, 'restored')

    def test_remove_free(self):
        self.assertEqual(self.parkbox.state, 'free')
        self.parkbox.remove()
        self.parkbox.save()
        self.parkbox.refresh_from_db()
        self.assertEqual(self.parkbox.state, 'removed')
        hist_entry = ParkboxHistory.objects.filter(
            parkbox=self.parkbox).latest('created_at')
        self.assertEqual(hist_entry.state, 'removed')

    def test_remove_disassociated(self):
        parkbox = ParkboxFactory.create(state='disassociated')
        self.assertEqual(parkbox.state, 'disassociated')
        parkbox.remove()
        parkbox.save()
        parkbox.refresh_from_db()
        self.assertEqual(parkbox.state, 'removed')
        hist_entry = ParkboxHistory.objects.filter(
            parkbox=parkbox).latest('created_at')
        self.assertEqual(hist_entry.state, 'removed')

    def test_remove_restored(self):
        parkbox = ParkboxFactory.create(state='restored')
        self.assertEqual(parkbox.state, 'restored')
        parkbox.remove()
        parkbox.save()
        parkbox.refresh_from_db()
        self.assertEqual(parkbox.state, 'removed')
        hist_entry = ParkboxHistory.objects.filter(
            parkbox=parkbox).latest('created_at')
        self.assertEqual(hist_entry.state, 'removed')
