from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from service.utils.asset import parse_asset_data
from service.utils.storage_handler import SystemFileStorage
from service.utils.telemetry import parse_telemetry_data
from .models import Asset, TelemetryPosition
from .serializers import AssetSerializer
from .models import Mission
from .serializers import MissionSerializer
from .models import Frame
from .serializers import FrameSerializer
from .models import Anomaly
from .serializers import ObjectSerializer
from .models import TelemetryAttribute
from .serializers import TelemetrySerializer

# from .models import TelemetryData
# from .serializers import TelemetryDataSerializer
# from .models import MissionData
# from .serializers import MissionDataSerializer
# from .models import VideoData
# from .serializers import VideoDataSerializer
from .utils.nested import NestedViewSetMixin
from .utils.nested import ParentDescriptor
from .utils.file import FileHandlerMixin
# from .tasks import handle_telemetry_data_file
from .tasks import handle_mission_data_file
from .tasks import handle_video_data_file
from django.conf import settings
import errno

import zipfile
import os


class AssetViewSet(ModelViewSet):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer


class MissionViewSet(ModelViewSet):
    queryset = Mission.objects.all()
    serializer_class = MissionSerializer

    def list(self, request, *args, **kwargs):
        return Response(self.serializer_class(self.queryset, many=True).data)

    def create(self, request, *args, **kwargs):
        file_type = 'application/zip'
        file = self.request.FILES.get('video_file')
        file_name = file.name
        temporary_file_location = os.path.join(settings.MEDIA_ROOT, self.kwargs.get('asset_uuid'), file_name)
        storage_manager = SystemFileStorage(file_name, temporary_file_location)
        storage_manager.save_temporary_file(file)
        storage_manager.unzip_file()
        m = Mission()
        m.asset_id = self.kwargs.get('asset_uuid')
        video_file = storage_manager.get_video_file()
        m.video_file.save(video_file.name.split('/')[-1], video_file)
        with storage_manager.get_telem_file() as telem:
            telemetry = parse_telemetry_data(telem)
            for telem_attribute in telemetry.attributes:
                values = telem_attribute.__dict__
                values.update({'mission': m})
                TelemetryAttribute.objects.create(**values)

            for telem_pos in telemetry.positions:
                values = telem_pos.__dict__
                values.update({'mission': m})
                TelemetryPosition.objects.create(**values)

        with storage_manager.get_xml_file() as xml:
            for frame in parse_asset_data(xml).frames:
                frame.create_db_entity(m)

        storage_manager.delete_temporary_files()

    def __create_target_dir(self, file_path):
        if not os.path.exists(os.path.dirname(file_path)):
            try:
                os.makedirs(os.path.dirname(file_path))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

    def __handle_uploaded_file(self, file, temp_location):
        self.__create_target_dir(temp_location)
        with open(temp_location, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

    def __unzip_file(self, zip_file_path):
        self.__create_target_dir(zip_file_path.split('.')[0])
        zip_ref = zipfile.ZipFile(zip_file_path, 'r')

        zip_ref.extractall(zip_file_path.split('.')[0])

    def __delete_temporary_file(self, zip_file_path):
        pass

    def __extract_telem_data(self, zip_file_path):
        pass

    def __extract_frames_data(self, zip_file_path):
        pass


class FrameViewSet(NestedViewSetMixin):
    queryset = Frame.objects.all()
    serializer_class = FrameSerializer
    parent_descriptor = ParentDescriptor(
        class_=Mission,
        pk_name='mission_pk',
        attr_name='mission'
    )


class ObjectViewSet(NestedViewSetMixin):
    queryset = Anomaly.objects.all()
    serializer_class = ObjectSerializer
    parent_descriptor = ParentDescriptor(
        class_=Frame,
        pk_name='frame_pk',
        attr_name='frame'
    )


class TelemetryViewSet(NestedViewSetMixin):
    queryset = TelemetryAttribute.objects.all()
    serializer_class = TelemetrySerializer
    parent_descriptor = ParentDescriptor(
        class_=Mission,
        pk_name='mission_pk',
        attr_name='mission'
    )

# class TelemetryDataViewSet(FileHandlerMixin):
#     queryset = TelemetryData.objects.all()
#     serializer_class = TelemetryDataSerializer
#     parent_descriptor = ParentDescriptor(
#         class_=Mission,
#         pk_name='mission_pk',
#         attr_name='mission'
#     )
#     file_handler = handle_telemetry_data_file


# class MissionDataViewSet(FileHandlerMixin):
#     queryset = MissionData.objects.all()
#     serializer_class = MissionDataSerializer
#     parent_descriptor = ParentDescriptor(
#         class_=Mission,
#         pk_name='mission_pk',
#         attr_name='mission'
#     )
#     file_handler = handle_mission_data_file


# class VideoDataViewSet(FileHandlerMixin):
#     queryset = VideoData.objects.all()
#     serializer_class = VideoDataSerializer
#     parent_descriptor = ParentDescriptor(
#         class_=Mission,
#         pk_name='mission_pk',
#         attr_name='mission'
#     )
#     file_handler = handle_video_data_file
