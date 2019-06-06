from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from service.models import Asset


class Test(APITestCase):
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
        Asset.objects.delete()
        url = reverse('assets-list')
        data = {
            "type": "PIP",
            "name": "test1",
            "created": "2019-06-06T14:25:26.870301Z",
            "modified": "2019-06-06T14:25:26.870433Z",
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
        self.assertEqual(Asset.objects.count(), 1)