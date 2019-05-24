from django.db.models import Model
from django.db.models import CharField
from django.db.models import TextField
from django.db.models import DateTimeField
from django.db.models import ForeignKey
from django.db.models import CASCADE
from django.db.models import FloatField
from django.db.models import UUIDField
from uuid import uuid4
from django.contrib.gis.db.models import PointField
from django.db.models import IntegerField
from django.db.models import FileField
from django.conf import settings
from django.contrib.gis.db.models import GeometryField, LineStringField
from django.utils.translation import gettext as _
from datetime import datetime


def upload_to(instance, file_name):
    return f'{instance.id}/{file_name}'

def default_asset_name():
    return f'{_("Asset")}_{datetime.utcnow()}'

def default_mission_name():
    return f'{_("Mission")}_{datetime.utcnow()}'


class Asset(Model):
    """Top level class for entire class hierarchy"""

    class Meta:
        db_table = "asset"

    """Asset type can take following values:
            - pipeline
            - power line
            - electric truss
    """

    PIPELINE = 'PIP'
    POWER_LINE = 'POW'
    ELECTRIC_TRUSS = 'ELE'

    TYPE_CHOICES = (
        (PIPELINE, 'Pipeline'),
        (POWER_LINE, 'Power line'),
        (ELECTRIC_TRUSS, 'Electric truss'),
    )

    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    type = CharField(max_length=3, choices=TYPE_CHOICES, blank=False, null=False)
    name = CharField(max_length=120, blank=False, null=False, default=default_asset_name)
    created = DateTimeField(auto_now_add=True)
    modified = DateTimeField(auto_now=True)
    description = TextField(blank=True, null=True)
    note = TextField(blank=True, null=True)
    geometry = GeometryField(blank=True, null=True, srid=settings.DEFAULT_SRID)


class Mission(Model):
    """All data is associated with Mission class, multiply missions can be attached to a single asset"""

    class Meta:
        db_table = "mission"

    asset = ForeignKey(Asset, related_name='missions', on_delete=CASCADE)

    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    name = CharField(max_length=120, blank=False, null=False, default=default_mission_name)
    description = TextField(blank=True, null=True)
    note = TextField(blank=True, null=True)
    created = DateTimeField(auto_now_add=True)
    geometry = GeometryField(blank=True, null=True, srid=settings.DEFAULT_SRID)
    video_file = FileField(upload_to=upload_to)



class Frame(Model):
    """Video frame object"""

    class Meta:
        db_table = "frame"

    mission = ForeignKey(Mission, related_name='frames', on_delete=CASCADE)

    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    index = IntegerField(blank=False, null=False)

    longitude = FloatField(blank=False, null=False, default=0)
    latitude = FloatField(blank=False, null=False, default=0)
    width = IntegerField(blank=False, null=False, default=0)
    height = IntegerField(blank=False, null=False, default=0)
    depth = IntegerField(blank=False, null=False, default=0)



class Anomaly(Model):
    """Some object of interest inside the frame"""

    class Meta:
        db_table = "anomaly"

    """Object type, up to now there's only one option:
            - insulator
    """

    INSULATOR = 'INS'

    TYPE_CHOICES = (
        (INSULATOR, 'Insulator'),
    )

    UNKNOWN = 'UNK'

    STATUS_CHOICES = (
        (UNKNOWN, 'Unknown'),
    )

    frame = ForeignKey(Frame, related_name='_anomalies', on_delete=CASCADE)

    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    type = CharField(max_length=3, choices=TYPE_CHOICES)
    status = CharField(max_length=3, choices=STATUS_CHOICES)
    confidence = IntegerField(blank=False, null=False)

    x_min = IntegerField(blank=False, null=False)
    x_max = IntegerField(blank=False, null=False)
    y_min = IntegerField(blank=False, null=False)
    y_max = IntegerField(blank=False, null=False)


class TelemetryAttribute(Model):
    """Telemetry data received from drone"""

    class Meta:
        db_table = "telemetry_attribute"

    mission = ForeignKey(Mission, related_name='telemetries_att', on_delete=CASCADE)

    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    time = IntegerField(blank=True, null=True)
    roll = FloatField(blank=True, null=True)
    pitch = FloatField(blank=True, null=True)
    yaw = FloatField(blank=True, null=True)
    roll_speed = FloatField(blank=True, null=True)
    pitch_speed = FloatField(blank=True, null=True)
    yaw_speed = FloatField(blank=True, null=True)


class TelemetryPosition(Model):

    class Meta:
        db_table = "telemetry_position"

    mission = ForeignKey(Mission, related_name='telemetries_pos', on_delete=CASCADE)

    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    time = IntegerField(blank=True, null=True)
    altitude = FloatField(blank=True, null=True)
    relative_altitude = FloatField(blank=True, null=True)
    longitude = FloatField(blank=True, null=True)
    latitude = FloatField(blank=True, null=True)


class VideoTable(Model):

    class Meta:
        db_table = "mission_video"

    mission = ForeignKey(Mission, related_name='video_mission', on_delete=CASCADE)
    width = IntegerField()
    height = IntegerField()
    depth = IntegerField()
    video_file = FileField(upload_to=upload_to)