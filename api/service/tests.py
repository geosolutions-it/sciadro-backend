from django.contrib.gis.geos import Point
from django.test import TestCase
from service.models import Asset
from service.models import Mission
from service.models import Frame
from service.models import Object
from service.models import Telemetry
from service.models import MissionData
from service.models import VideoData


class BasicModelTest(TestCase):
    def setUp(self) -> None:
        VideoData.objects.all().delete()
        MissionData.objects.all().delete()
        Telemetry.objects.all().delete()
        Object.objects.all().delete()
        Frame.objects.all().delete()
        Mission.objects.all().delete()
        Asset.objects.all().delete()

    def test_basic_model_creation(self):
        asset = Asset()
        asset.save()
        mission = Mission(asset=asset)
        mission.save()
        frame = Frame(mission=mission, index=0, location=Point())
        frame.save()
        object_ = Object(frame=frame, confidence=0, x_min=0, x_max=0, y_min=0, y_max=0)
        object_.save()
        telemetry = Telemetry(mission=mission)
        telemetry.save()
        mission_data = MissionData(mission=mission)
        mission_data.save()
        video_data = VideoData(mission=mission)
        video_data.save()
