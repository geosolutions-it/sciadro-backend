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
    to_remove = mission.mission_file.mission_file.path
    output = f'{mission.mission_file.mission_file.path.split(".")[0]}.{"mp4"}'
    p = subprocess.Popen(f'ffmpeg -i {mission.mission_file.mission_file.path} {output}', stdout=subprocess.PIPE,
                         shell=True)
    o, e = p.communicate()
    with open(output, 'rb') as mp4_file:
        mission.mission_file.mission_file.save(f'{output.split("/")[-1]}', mp4_file)
    try:
        command = ['ffprobe', mission.mission_file.mission_file.path, '-v', '0', '-select_streams', 'v', '-print_format',
                   'flat', '-show_entries', 'stream=r_frame_rate']
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        o, e = p.communicate()
        rate = o.split('=')[1].strip()[1:-1].split('/')
        if len(rate) == 1:
            mission.mission_file.fps = float(rate[0])
        elif len(rate) == 2:
            mission.mission_file.fps = float(rate[0]) / float(rate[1])
        mission.mission_file.save()
    except:
        pass
    os.remove(to_remove)
    os.remove(output)
    return True
