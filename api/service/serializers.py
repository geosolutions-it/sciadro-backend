import json

from django.contrib.gis.geos import LineString, Point
from rest_framework.serializers import ModelSerializer, SerializerMethodField, JSONField, IntegerField, FileField, CharField

from .models import Asset, TelemetryPosition, MissionVideo
from .models import Mission
from .models import Frame
from .models import Anomaly
from .models import TelemetryAttribute


class GeometryField(JSONField):

    def to_representation(self, value):
        if value.geometry:
            return json.loads(value.geometry.geojson)
        return {}

    def to_internal_value(self, data):
        if isinstance(data, str):
            geom_json = json.loads(data)
        else:
            geom_json = data
        if geom_json:
            coords = geom_json.get('coordinates')
            ret = {
                "geometry": Point(coords) if geom_json.get('type') == 'Point' else LineString(coords)
            }
            return ret
        return {}


class MissionVideoSerializer(ModelSerializer):
    mission_file_url = SerializerMethodField()
    mission_file = FileField(write_only=True)

    class Meta:
        model = MissionVideo
        fields = ('id', 'width', 'height', 'mission_file', 'fps', 'mime_type', 'mission_file_url')
        read_only_fields = ('width', 'height', 'fps', 'mime_type')

    def get_mission_file_url(self, obj):
        return f'''{self.context.get("request").scheme}://{self.context.get("request").META.get(
            "HTTP_HOST")}/{obj.mission_file.url}'''


class MissionVideoNarrowSerializer(ModelSerializer):
    class Meta:
        model = MissionVideo
        fields = ('id',)


class AssetSerializer(ModelSerializer):
    geometry = GeometryField(source='*')
    type_name = SerializerMethodField()
    name = CharField(required=True)

    class Meta:
        model = Asset
        fields = ('id', 'type', 'name', 'created', 'modified', 'description', 'note', 'geometry',
                  'missions', 'type_name')
        read_only_fields = ('missions',)

    def get_type_name(self, obj):
        return list(filter(lambda x: x[0] == obj.type, Asset.TYPE_CHOICES))[0][1]


class MissionSerializer(ModelSerializer):
    geometry = SerializerMethodField()
    mission_file = MissionVideoSerializer()

    name = CharField(required=True)

    class Meta:
        model = Mission
        fields = ('id', 'created', 'name', 'description', 'note', 'geometry', 'asset', 'mission_file', 'modified')
        read_only_fields = ('asset', 'geometry')

    def get_geometry(self, obj):
        if obj.geometry:
            return json.loads(obj.geometry.geojson)
        else:
            return {}


class MissionNarrowSerializer(ModelSerializer):
    geometry = SerializerMethodField()
    mission_file = MissionVideoNarrowSerializer()

    class Meta:
        model = Mission
        fields = ('id', 'created', 'name', 'description', 'note', 'geometry', 'asset', 'mission_file', 'modified')
        read_only_fields = ('asset', 'geometry')

    def get_geometry(self, obj):
        if obj.geometry:
            return json.loads(obj.geometry.geojson)
        else:
            return {}


class FrameSerializer(ModelSerializer):
    class Meta:
        model = Frame
        fields = ('id', 'mission', 'index', '_anomalies', 'longitude', 'latitude')
        read_only_fields = ('mission', '_anomalies')


class AnomalySerializer(ModelSerializer):
    type_name = SerializerMethodField()
    status_name = SerializerMethodField()
    xmax = IntegerField(source='x_max')
    xmin = IntegerField(source='x_min')
    ymax = IntegerField(source='y_max')
    ymin = IntegerField(source='y_min')

    class Meta:
        model = Anomaly
        fields = (
            'id', 'type', 'status', 'confidence', 'frame', 'xmax', 'xmin', 'ymax', 'ymin', 'type_name', 'status_name')
        read_only_fields = ('frame',)

    def get_type_name(self, obj):
        return list(filter(lambda x: x[0] == obj.type, Anomaly.TYPE_CHOICES))[0][1]

    def get_status_name(self, obj):
        return list(filter(lambda x: x[0] == obj.status, Anomaly.STATUS_CHOICES))[0][1]


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
