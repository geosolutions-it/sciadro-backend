from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from service.models import Asset


class TestAssetCRUD(APITestCase):
    fixtures = ['asset', ]

    def test_asset_list(self):
        url = reverse('assets-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json().get('results', [])), 1)

    def test_asset_detail(self):
        url = reverse('assets-detail', kwargs={
            'pk': '783cc226-bf04-4ef1-8b32-667888b6378b'
        })
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_asset_delete(self):
        url = reverse('assets-detail', kwargs={
            'pk': '783cc226-bf04-4ef1-8b32-667888b6378b'
        })
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Asset.objects.count(), 0)

    def test_asset_create_valid_data(self):
        url = reverse('assets-list')
        data = {
            "type": "PIP",
            "name": "test1",
            "description": "TESTDESC",
            "note": "TEST ASSET",
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [
                        10.4374221,
                        43.6524748
                    ],
                    [
                        1.0,
                        2.0
                    ]
                ]
            },
            "missions": [],
            "type_name": "Pipeline"
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Asset.objects.count(), 2)

    def test_asset_create_invalid_data(self):
        url = reverse('assets-list')
        data = {
            "type": "PIP",
            "name": None,
            "description": "TESTDESC",
            "note": "TEST ASSET",
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [
                        10.4374221,
                        43.6524748
                    ],
                    [
                        1.0,
                        2.0
                    ]
                ]
            },
            "missions": [],
            "type_name": "Pipeline"
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Asset.objects.count(), 1)


class TestMissionCRUD(APITestCase):

    fixtures = ['mission']

    #todo: to test mission creation, consider unit testing wit file mock

    def test_mission_list(self):
        url = reverse('missions-list', kwargs={
            'asset_uuid': '3d1ab96d-7b7c-4c95-8c5b-ade2d20e0919'
        })
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json().get('results', [])), 1)

    def test_mission_detail(self):
        url = reverse('missions-detail', kwargs={
            'asset_uuid': '3d1ab96d-7b7c-4c95-8c5b-ade2d20e0919',
            'pk': 'd69032c2-3e3d-408b-9880-1e36a58203ba'
        })
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class Test