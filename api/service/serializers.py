from rest_framework.serializers import ModelSerializer
from .models import Asset
from .models import Mission
from .models import Frame
from .models import Object
from .models import Telemetry


class AssetSerializer(ModelSerializer):
    class Meta:
        model = Asset
        fields = ('id', 'type', 'name', 'created', 'modified', 'description', 'note', 'point', 'line')
        read_only_fields = ('id',)


class MissionSerializer(ModelSerializer):
    class Meta:
        model = Mission
        fields = ('asset', 'id', 'name', 'description', 'note', 'created', 'point', 'line')
        read_only_fields = ('id',)


class FrameSerializer(ModelSerializer):
    class Meta:
        model = Frame
        fields = ('mission', 'id', 'index', 'location', 'point', 'line')
        read_only_fields = ('id',)


class ObjectSerializer(ModelSerializer):
    class Meta:
        model = Object
        fields = ('frame', 'id', 'type', 'status', 'confidence', 'box')
        read_only_fields = ('id',)


class TelemetrySerializer(ModelSerializer):
    class Meta:
        model = Telemetry
        fields = ('mission', 'id', 'time', 'roll', 'pitch', 'yaw', 'roll_speed', 'pitch_speed', 'yaw_speed', 'altitude',
                  'relative_altitude', 'location')
        read_only_fields = ('id',)
