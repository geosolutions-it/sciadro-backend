from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from service.models import Asset, Mission
from service.utils.asset import Frame, Id, Position, Size, Anomaly, Status, Box
from service.models import Frame as DBFrame
from service.models import Anomaly as DBAnomaly


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

    # todo: to test mission creation, consider unit testing with file mock

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


class TestFrameCRUD(APITestCase):
    fixtures = ['frame']

    def test_frame_list(self):
        url = reverse('frame-list', kwargs={
            'asset_uuid': 'e2b2ee0e-afc5-4e45-aec6-47de731a1afc',
            'mission_uuid': 'c4f0331c-c68c-4d1a-8966-8c44a076d2a6'

        })
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json().get('results', [])), 4)

    def test_frame_detail(self):
        url = reverse('frame-detail', kwargs={
            'asset_uuid': 'e2b2ee0e-afc5-4e45-aec6-47de731a1afc',
            'mission_uuid': 'c4f0331c-c68c-4d1a-8966-8c44a076d2a6',
            'pk': '4d127d35-7fc3-4ed7-b443-b195f73f9559'
        })
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_new_frame(self):
        frames_count = DBFrame.objects.count()
        f = Frame(
            id=Id(
                index=36,
                database='Unknown'
            ),
            position=Position(
                longitude=10.4374,
                latitude=43.6525
            ),
            size=Size(
                width=1024,
                height=768,
                depth=3
            ),
            anomalies=[
            ]
        )
        f.create_db_entity(Mission.objects.get(pk='c4f0331c-c68c-4d1a-8966-8c44a076d2a6'))
        self.assertGreater(DBFrame.objects.count(), frames_count)


class TestAnomalyCRUD(APITestCase):
    fixtures = ['anomaly']

    def test_anomaly_list(self):
        url = reverse('anomaly-list', kwargs={
            'asset_uuid': '7d998bb5-e251-4f65-bc0e-9cd4c5874c60',
            'mission_uuid': 'cd46ea46-b1c4-425e-bd43-8174bcac8034',
            'frame_uuid': 'c4f2eec3-1959-4819-9b4a-d1f910228bfd'

        })
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json().get('results', [])), 1)

    def test_anomaly_detail(self):
        url = reverse('anomaly-detail', kwargs={
            'asset_uuid': '7d998bb5-e251-4f65-bc0e-9cd4c5874c60',
            'mission_uuid': 'cd46ea46-b1c4-425e-bd43-8174bcac8034',
            'frame_uuid': 'c4f2eec3-1959-4819-9b4a-d1f910228bfd',
            'pk': '025e5726-12c8-4786-98ec-3953b38d54ac'
        })
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_anomalies(self):
        url = reverse('mission_anomalies-list', kwargs={
            'asset_uuid': '7d998bb5-e251-4f65-bc0e-9cd4c5874c60',
            'mission_uuid': 'cd46ea46-b1c4-425e-bd43-8174bcac8034',

        })
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json().get('results', [])), 3)

    def test_create_new_anomaly(self):
        anomalies_count = DBAnomaly.objects.count()
        f_with_anomalies = Frame(
            id=Id(
                index=36,
                database='Unknown'
            ),
            position=Position(
                longitude=10.4374,
                latitude=43.6525
            ),
            size=Size(
                width=1024,
                height=768,
                depth=3
            ),
            anomalies=[
                Anomaly(
                    id=1,
                    type='insulator',
                    status=Status(
                        class_='Unknown',
                        confidence=0
                    ),
                    box=Box(
                        x_min=475,
                        y_min=42,
                        x_max=518,
                        y_max=233
                    )
                ),
                Anomaly(
                    id=2,
                    type='insulator',
                    status=Status(
                        class_='Unknown',
                        confidence=0
                    ),
                    box=Box(
                        x_min=475,
                        y_min=42,
                        x_max=518,
                        y_max=233
                    )
                )
            ]
        )
        f_with_anomalies.create_db_entity(Mission.objects.get(pk='cd46ea46-b1c4-425e-bd43-8174bcac8034'))
        self.assertGreater(DBAnomaly.objects.count(), anomalies_count)


class TestTelemetryCRUD(APITestCase):
    fixtures = ['telemetry_att', 'telemetry_pos']

    def test_telemetry_list(self):
        url = reverse('telemetry-list', kwargs={
            'asset_uuid': '7d998bb5-e251-4f65-bc0e-9cd4c5874c60',
            'mission_uuid': 'cd46ea46-b1c4-425e-bd43-8174bcac8034',

        })
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json().get('telemetry_attributes', [])), 3)
        self.assertEqual(len(response.json().get('telemetry_positions', [])), 3)

    def test_telemetry_detail(self):
        url = reverse('telemetry-detail', kwargs={
            'asset_uuid': '7d998bb5-e251-4f65-bc0e-9cd4c5874c60',
            'mission_uuid': 'cd46ea46-b1c4-425e-bd43-8174bcac8034',
            'pk': 'fac0b6ff-f2be-4974-a037-8d8aa6385c6f'
        }) + '?type=pos'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = reverse('telemetry-detail', kwargs={
            'asset_uuid': '7d998bb5-e251-4f65-bc0e-9cd4c5874c60',
            'mission_uuid': 'cd46ea46-b1c4-425e-bd43-8174bcac8034',
            'pk': '13a9a556-d787-42af-9292-fa2f34e9b6a8'
        }) + '?type=att'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


