from django.test import TestCase

from polls.models import Address
import polls.tests.config as test_config


class AddressTest(TestCase):

    def test_address_creation(self):
        address = Address.objects.create(**test_config.ADDRESS)
        self.assertTrue(isinstance(address, Address))
        self.assertEquals(1, Address.objects.count())
