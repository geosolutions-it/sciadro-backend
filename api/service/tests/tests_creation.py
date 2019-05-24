from django.contrib.gis.geos import Point
from django.test import TestCase
from service.models import Asset
from service.models import Mission
from service.models import Frame
from service.models import Anomaly
from service.models import TelemetryAttribute


class BasicModelTest(TestCase):
    def setUp(self) -> None:
        """Remove all records from DB to get reliable test results"""
        TelemetryAttribute.objects.all().delete()
        Anomaly.objects.all().delete()
        Frame.objects.all().delete()
        Mission.objects.all().delete()
        Asset.objects.all().delete()

    def test_basic_model_creation(self):
        """Create a basic DB record set"""
        asset = Asset()
        asset.save()
        mission = Mission(asset=asset)
        mission.save()
        frame = Frame(mission=mission, index=0, longitude=0.0, latitude=0.0)
        frame.save()
        object_ = Anomaly(frame=frame, confidence=0, x_min=0, x_max=0, y_min=0, y_max=0)
        object_.save()
        telemetry = TelemetryAttribute(mission=mission)
        telemetry.save()
