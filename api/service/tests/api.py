from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from service.models import Asset
from service.models import Mission


def clear_db():
    Asset.objects.all().delete()
    Mission.objects.all().delete()


class BaseTest(APITestCase):
    def setUp(self) -> None:
        clear_db()


class AssetTests(BaseTest):
    def test_create_asset(self) -> None:
        response = self.client.post(
            reverse('assets-list'),
            {},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Asset.objects.count(), 1)


class MissionTests(BaseTest):
    def test_create_mission(self) -> None:
        response = self.client.post(
            reverse('assets-list'),
            {},
            format='json'
        )
        asset_pk = response.data['id']
        response = self.client.post(
            reverse('missions-list', kwargs={'asset_pk': asset_pk}),
            {},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Mission.objects.count(), 1)
