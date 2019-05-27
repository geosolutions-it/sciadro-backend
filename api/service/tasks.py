import subprocess
from enum import Enum

from .models import Mission
import os
from api.celery import app


class TASK_ENUM(Enum):
    CONVERSION = 'CONVERSION'


@app.task(bind=True)
def convert_avi_to_mp4(self, mission_uuid):
    mission = Mission.objects.get(id=mission_uuid)
    to_remove = mission.mission_video.video_file.path
    output = f'{mission.mission_video.video_file.path.split(".")[0]}.{"mp4"}'
    p = subprocess.Popen(f'ffmpeg -i {mission.mission_video.video_file.path} {output}', stdout=subprocess.PIPE, shell=True)
    o,e = p.communicate()
    with open(output, 'rb') as mp4_file:
        mission.mission_video.video_file.save(f'{output.split("/")[-1]}', mp4_file)
    os.remove(to_remove)
    os.remove(output)
    return True



