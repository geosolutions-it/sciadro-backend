import json

from django.contrib.gis.geos import LineString, Point
from rest_framework.serializers import ModelSerializer, SerializerMethodField, JSONField

from .models import Asset, TelemetryPosition, MissionVideo
from .models import Mission
from .models import Frame
from .models import Anomaly
from .models import TelemetryAttribute


class GeometryField(JSONField):

    def to_representation(self, value):
        if value.geometry:
            return json.loads(value.geometry.geojson)
        return []

    def to_internal_value(self, data):
        geom_json = json.loads(data)
        if geom_json:
            coords = geom_json.get('coordinates')
            ret = {
                "geometry": LineString(coords) if len(coords) > 1 else Point(coords[0])
            }
            return ret
        return []


class MissionVideoSerializer(ModelSerializer):
    class Meta:
        model = MissionVideo
        fields = ('width', 'height', 'depth', 'video_file', 'fps', 'mime_type')
        read_only_fields = ('width', 'height', 'depth', 'fps', 'mime_type')


class AssetSerializer(ModelSerializer):
    geometry = GeometryField(source='*')

    class Meta:
        model = Asset
        fields = ('id', 'type', 'name', 'created', 'modified', 'description', 'note', 'geometry',
                  'missions')
        read_only_fields = ('missions',)


class MissionSerializer(ModelSerializer):
    geometry = SerializerMethodField()
    mission_video = MissionVideoSerializer()

    class Meta:
        model = Mission
        fields = (
            'id', 'created', 'name', 'description', 'note', 'geometry', 'asset', 'frames', 'telemetries_att',
            'telemetries_pos', 'mission_video')
        read_only_fields = ('asset', 'frames', 'telemetries_att', 'telemetries_pos', 'geometry')

    def get_geometry(self, obj):
        return json.loads(obj.geometry.geojson)


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
