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
from django.contrib.gis.db.models import PolygonField
from django.contrib.gis.db.models import LineStringField
from django.db.models import FileField
from api.settings import DEFAULT_SRID


class Asset(Model):
    class Meta:
        db_table = "assets"

    PIPELINE = 'PIP'
    POWER_LINE = 'POW'
    ELECTRIC_TRUSS = 'ELE'

    TYPE_CHOICES = (
        (PIPELINE, 'Pipeline'),
        (POWER_LINE, 'Power line'),
        (ELECTRIC_TRUSS, 'Electric truss'),
    )

    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    type = CharField(max_length=3, choices=TYPE_CHOICES, blank=False, null=True)
    name = CharField(max_length=120, blank=True, null=True)
    created = DateTimeField(auto_now_add=True)
    modified = DateTimeField(auto_now=True)
    description = TextField(blank=True, null=True)
    note = TextField(blank=True, null=True)
    # Geometry
    point = PointField(blank=True, null=True, srid=DEFAULT_SRID)
    # or
    line = LineStringField(blank=True, null=True, srid=DEFAULT_SRID)


class Mission(Model):
    class Meta:
        db_table = "missions"

    asset = ForeignKey(Asset, related_name='missions', on_delete=CASCADE)

    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    name = CharField(max_length=120, blank=True, null=True)
    description = TextField(blank=True, null=True)
    note = TextField(blank=True, null=True)
    created = DateTimeField(auto_now_add=True)
    # Geometry (path, point)
    point = PointField(blank=True, null=True, srid=DEFAULT_SRID)
    # or
    line = LineStringField(blank=True, null=True, srid=DEFAULT_SRID)


class Frame(Model):
    class Meta:
        db_table = "frames"

    mission = ForeignKey(Mission, related_name='frames', on_delete=CASCADE)

    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    index = IntegerField(blank=False, null=False)
    # Coordinates
    location = PointField(blank=False, null=False, srid=DEFAULT_SRID)
    # Geometry
    point = PointField(blank=True, null=True, dim=3, srid=DEFAULT_SRID)
    # or
    line = LineStringField(blank=True, null=True, dim=3, srid=DEFAULT_SRID)


class Object(Model):
    class Meta:
        db_table = "objects"

    INSULATOR = 'INS'

    TYPE_CHOICES = (
        (INSULATOR, 'Insulator'),
    )

    UNKNOWN = 'UNK'

    STATUS_CHOICES = (
        (UNKNOWN, 'Unknown'),
    )

    frame = ForeignKey(Frame, related_name='_objects', on_delete=CASCADE)

    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    type = CharField(max_length=3, choices=TYPE_CHOICES)
    status = CharField(max_length=3, choices=STATUS_CHOICES)
    confidence = IntegerField(blank=False, null=False)
    box = PolygonField(blank=False, null=False, srid=DEFAULT_SRID)


class Telemetry(Model):
    class Meta:
        db_table = "telemetries"

    mission = ForeignKey(Mission, related_name='telemetries', on_delete=CASCADE)

    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    time = IntegerField(blank=True, null=True)
    roll = FloatField(blank=True, null=True)
    pitch = FloatField(blank=True, null=True)
    yaw = FloatField(blank=True, null=True)
    roll_speed = FloatField(blank=True, null=True)
    pitch_speed = FloatField(blank=True, null=True)
    yaw_speed = FloatField(blank=True, null=True)
    altitude = FloatField(blank=True, null=True)
    relative_altitude = FloatField(blank=True, null=True)
    # longitude, latitude
    location = PointField(blank=True, null=True, srid=DEFAULT_SRID)


UPLOADED = 'UPL'
PROCESSED = 'PRO'

FILE_STATUS_CHOICES = (
    (UPLOADED, 'Uploaded'),
    (PROCESSED, 'Processed')
)


def upload_to(instance, file_name):
    return f'{instance.mission.id}/{file_name}'


class TelemetryData(Model):
    class Meta:
        db_table = "telemetry_data"

    mission = ForeignKey(Mission, related_name='telemetry_files', on_delete=CASCADE)

    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    created = DateTimeField(auto_now_add=True)
    status = CharField(max_length=3, choices=FILE_STATUS_CHOICES, default=UPLOADED)
    file = FileField(upload_to=upload_to)


class MissionData(Model):
    class Meta:
        db_table = "mission_data"

    mission = ForeignKey(Mission, related_name='mission_files', on_delete=CASCADE)

    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    created = DateTimeField(auto_now_add=True)
    status = CharField(max_length=3, choices=FILE_STATUS_CHOICES, default=UPLOADED)
    file = FileField(upload_to=upload_to)


class VideoData(Model):
    class Meta:
        db_table = "video_data"

    mission = ForeignKey(Mission, related_name='video_files', on_delete=CASCADE)

    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    created = DateTimeField(auto_now_add=True)
    status = CharField(max_length=3, choices=FILE_STATUS_CHOICES, default=UPLOADED)
    file = FileField(upload_to=upload_to)
