from rest_framework.serializers import ModelSerializer
from .models import Asset
from .models import Mission
from .models import Frame
from .models import Object
from .models import Telemetry
from .models import TelemetryData
from .models import AssetData
from .models import VideoData


class MissionSerializer(ModelSerializer):
    class Meta:
        model = Mission
        fields = ('id', 'created', 'name', 'description', 'note', 'point', 'line', 'assets')


class AssetSerializer(ModelSerializer):
    class Meta:
        model = Asset
        fields = ('id', 'mission', 'type', 'name', 'created', 'modified', 'description', 'note', 'point', 'line',
                  'frames', 'telemetries')


class FrameSerializer(ModelSerializer):
    class Meta:
        model = Frame
        fields = ('id', 'point', 'line', 'asset', 'index', 'location', '_objects')


class ObjectSerializer(ModelSerializer):
    class Meta:
        model = Object
        fields = ('id', 'type', 'status', 'confidence', 'box')


class TelemetrySerializer(ModelSerializer):
    class Meta:
        model = Telemetry
        fields = ('id', 'asset', 'time', 'roll', 'pitch', 'yaw', 'roll_speed', 'pitch_speed', 'yaw_speed', 'altitude',
                  'relative_altitude', 'location')


class TelemetryDataSerializer(ModelSerializer):
    class Meta:
        model = TelemetryData
        fields = ('file', 'status')


class AssetDataSerializer(ModelSerializer):
    class Meta:
        model = AssetData
        fields = ('file', 'status')


class VideoDataSerializer(ModelSerializer):
    class Meta:
        model = VideoData
        fields = ('file', 'status')
