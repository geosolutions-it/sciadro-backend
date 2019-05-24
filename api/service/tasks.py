import subprocess
from enum import Enum

from celery import shared_task
from .models import Mission
from .models import Frame
from .models import Anomaly
from .utils.asset import parse_asset_data
from .utils.telemetry import parse_telemetry_data
from django.contrib.gis.geos import Point
from django.contrib.gis.geos import Polygon
from celery import current_task
import os
from api.celery import app


class TASK_ENUM(Enum):
    CONVERSION = 'CONVERSION'


@app.task(bind=True)
def convert_avi_to_mp4(self, mission_uuid):
    mission = Mission.objects.get(id=mission_uuid)
    to_remove = mission.video_file.path
    output = f'{mission.video_file.path.split(".")[0]}.{"mp4"}'
    p = subprocess.Popen(f'ffmpeg -i {mission.video_file.path} {output}', stdout=subprocess.PIPE, shell=True)
    o,e = p.communicate()
    with open(output, 'rb') as mp4_file:
        mission.video_file.save(f'{output.split("/")[-1]}', mp4_file)
    os.remove(to_remove)
    return True



# @shared_task(bind=True)
# def handle_telemetry_data_file(self, pk):
#     telemetry_data = TelemetryData.objects.get(pk=pk)
#     data = parse_telemetry_data(telemetry_data.file.path)
#     mission = Mission.objects.get(pk=telemetry_data.mission.id)
#
#     for attributes in data.attributes:
#         telemetry = Telemetry()
#         telemetry.mission = mission
#         telemetry.time = attributes.time
#         telemetry.roll = attributes.roll
#         telemetry.pitch = attributes.pitch
#         telemetry.yaw = attributes.yaw
#         telemetry.rollspeed = attributes.rollspeed
#         telemetry.pitchspeed = attributes.pitchspeed
#         telemetry.yawspeed = attributes.yawspeed
#         telemetry.save()
#
#     for position in data.positions:
#         telemetry = Telemetry()
#         telemetry.mission = mission
#         telemetry.time = position.time
#         telemetry.lat = position.lat
#         telemetry.lon = position.lon
#         telemetry.alt = position.alt
#         telemetry.relative_alt = position.relative_alt
#         telemetry.save()


@shared_task(bind=True)
def handle_mission_data_file(self, pk):
    pass
    # mission_data = MissionData.objects.get(pk=pk)
    # data = parse_asset_data(mission_data.file.path)
    # mission = Mission.objects.get(pk=mission_data.mission.id)
    #
    # for frame_data in data.frames:
    #     frame = Frame()
    #     frame.mission = mission
    #     frame.location = Point(
    #         x=frame_data.position.longitude,
    #         y=frame_data.position.latitude
    #     )
    #     frame.index = frame_data.id.index
    #     frame.save()
    #     for object_data in frame_data.objects:
    #         object_ = Object()
    #         object_.frame = frame
    #         if object_data.type == 'insulator':
    #             object_.type = object_.INSULATOR
    #         else:
    #             raise ValueError(f'Unknown object type: {object_data.type}')
    #         object_.confidence = object_data.status.confidence
    #         object_.box = Polygon((
    #             (object_data.box.x_min, object_data.box.y_min),
    #             (object_data.box.x_min, object_data.box.y_max),
    #             (object_data.box.x_max, object_data.box.y_max),
    #             (object_data.box.x_max, object_data.box.y_min),
    #             (object_data.box.x_min, object_data.box.y_min)
    #         ))
    #         object_.save()


@shared_task(bind=True)
def handle_video_data_file(self, pk):
    pass
