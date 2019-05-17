from rest_framework.serializers import ModelSerializer

from service.utils.telemetry import TelemetryPosition
from .models import Asset
from .models import Mission
from .models import Frame
from .models import Anomaly
from .models import TelemetryAttribute


class AssetSerializer(ModelSerializer):
    class Meta:
        model = Asset
        fields = ('id', 'type', 'name', 'created', 'modified', 'description', 'note', 'geometry',
                  'missions')
        read_only_fields = ('missions',)


class MissionSerializer(ModelSerializer):
    class Meta:
        model = Mission
        fields = (
            'id', 'created', 'name', 'description', 'note', 'geometry', 'asset', 'frames', 'telemetries_att',
            'video_file', 'telemetries_pos')
        read_only_fields = ('asset', 'frames', 'telemetries_att', 'telemetries_pos')


class FrameSerializer(ModelSerializer):
    class Meta:
        model = Frame
        fields = ('id', 'mission', 'index', '_anomalies', 'longitude', 'latitude')
        read_only_fields = ('mission', '_anomalies')


class AnomalySerializer(ModelSerializer):
    class Meta:
        model = Anomaly
        fields = ('id', 'type', 'status', 'confidence', 'x_min', 'frame', 'x_max', 'y_min', 'y_max')
        read_only_fields = ('frame',)


class TelemetrySerializer(ModelSerializer):
    class Meta:
        model = TelemetryAttribute
        fields = ('id', 'mission', 'time', 'roll', 'pitch', 'yaw', 'roll_speed', 'pitch_speed', 'yaw_speed')
        read_only_fields = ('mission',)


class TelemetryPositionSerializer(ModelSerializer):
    class Meta:
        model = TelemetryPosition
        fields = ('id', 'mission', 'time', 'altitude', 'relative_altitude', 'longitude', 'latitude')
        read_only_fields = ('mission',)
