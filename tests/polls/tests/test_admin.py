from django.contrib.auth.models import User
from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from polls.models import Address
import polls.tests.config as test_config

class AddressAdminTest(TestCase):

    def setUp(self):
        User.objects.create_superuser(**test_config.ADMIN_USER)

    def test_add_document_form(self):
        self.assertEquals(0, Address.objects.count())

        client = Client()
        client.login(**test_config.ADMIN_USER)
        change_url = reverse('admin:polls_address_add')
        data = test_config.ADDRESS
        response = client.post(change_url, data)
        self.assertEquals(1, Address.objects.count())
