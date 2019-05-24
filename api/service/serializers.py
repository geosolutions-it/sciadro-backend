import json

from django.contrib.gis.geos import LineString
from rest_framework.serializers import ModelSerializer, SerializerMethodField, JSONField

from .models import Asset, TelemetryPosition
from .models import Mission
from .models import Frame
from .models import Anomaly
from .models import TelemetryAttribute


class GeometryField(JSONField):

    def to_representation(self, value):
        if value.geometry:
            return value.geometry.array
        return []

    def to_internal_value(self, data):
        geom_json = json.loads(data)
        ret = {
            "geometry": LineString(geom_json.get('coordinates'))
        }
        return ret


class AssetSerializer(ModelSerializer):
    geometry = GeometryField(source='*')

    class Meta:
        model = Asset
        fields = ('id', 'type', 'name', 'created', 'modified', 'description', 'note', 'geometry',
                  'missions')
        read_only_fields = ('missions',)


class MissionSerializer(ModelSerializer):
    geometry = SerializerMethodField()

    class Meta:
        model = Mission
        fields = (
            'id', 'created', 'name', 'description', 'note', 'geometry', 'asset', 'frames', 'telemetries_att',
            'video_file', 'telemetries_pos')
        read_only_fields = ('asset', 'frames', 'telemetries_att', 'telemetries_pos', 'geometry')

    def get_geometry(self, obj):
        return obj.geometry.array


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
