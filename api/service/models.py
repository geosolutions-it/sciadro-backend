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


class Asset(Model):
    class Meta:
        db_table = "asset"

    PIPELINE = 'PIP'
    POWER_LINE = 'POW'
    ELECTRIC_TRUSS = 'ELE'

    TYPE_CHOICES = (
        (PIPELINE, 'Pipeline'),
        (POWER_LINE, 'Power line'),
        (ELECTRIC_TRUSS, 'Electric truss'),
    )

    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    type = CharField(max_length=3, choices=TYPE_CHOICES)
    name = CharField(max_length=120, blank=False, null=False)
    created = DateTimeField(auto_now_add=True)
    modified = DateTimeField(auto_now=True)
    description = TextField(blank=True, null=True)
    note = TextField(blank=True, null=True)
    # Geometry
    point = PointField(blank=True, null=True)
    # or
    line = LineStringField(blank=True, null=True)


class Mission(Model):
    class Meta:
        db_table = "mission"

    asset = ForeignKey("asset", on_delete=CASCADE)

    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    name = CharField(max_length=120, blank=True, null=True)
    description = TextField(blank=True, null=True)
    note = TextField(blank=True, null=True)
    created = DateTimeField(auto_now_add=True)
    # Geometry (path, point)
    point = PointField(blank=True, null=True)
    # or
    line = LineStringField(blank=True, null=True)


class Frame(Model):
    class Meta:
        db_table = "frame"

    mission = ForeignKey("mission", on_delete=CASCADE)

    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    index = IntegerField(blank=False, null=False)
    # Coordinates
    location = PointField(blank=False, null=False)
    # Geometry
    point = PointField(blank=True, null=True, dim=3)
    # or
    line = LineStringField(blank=True, null=True, dim=3)


class Object(Model):
    class Meta:
        db_table = "object"

    INSULATOR = 'INS'

    TYPE_CHOICES = (
        (INSULATOR, 'Insulator'),
    )

    UNKNOWN = 'UNK'

    STATUS_CHOICES = (
        (UNKNOWN, 'Unknown'),
    )

    frame = ForeignKey("frame", on_delete=CASCADE)

    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    type = CharField(max_length=3, choices=TYPE_CHOICES)
    status = CharField(max_length=3, choices=STATUS_CHOICES)
    confidence = IntegerField(blank=False, null=False)
    box = PolygonField(blank=False, null=False)


class Telemetry(Model):
    class Meta:
        db_table = "telemetry"

    mission = ForeignKey("mission", on_delete=CASCADE)

    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    time = DateTimeField(blank=False, null=False)
    roll = FloatField(blank=False, null=False)
    pitch = FloatField(blank=False, null=False)
    yaw = FloatField(blank=False, null=False)
    roll_speed = FloatField(blank=False, null=False)
    pitch_speed = FloatField(blank=False, null=False)
    yaw_speed = FloatField(blank=False, null=False)
    altitude = FloatField(blank=False, null=False)
    relative_altitude = FloatField(blank=False, null=False)
    # longitude, latitude
    location = PointField(blank=False, null=False)
