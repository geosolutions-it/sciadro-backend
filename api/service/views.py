from rest_framework.viewsets import ModelViewSet
from .models import Asset
from .serializers import AssetSerializer
from .models import Mission
from .serializers import MissionSerializer
from .models import Frame
from .serializers import FrameSerializer
from .models import Object
from .serializers import ObjectSerializer
from .models import Telemetry
from .serializers import TelemetrySerializer
# from .models import TelemetryData
# from .serializers import TelemetryDataSerializer
from .models import MissionData
from .serializers import MissionDataSerializer
from .models import VideoData
from .serializers import VideoDataSerializer
from .utils.nested import NestedViewSetMixin
from .utils.nested import ParentDescriptor
from .utils.file import FileHandlerMixin
# from .tasks import handle_telemetry_data_file
from .tasks import handle_mission_data_file
from .tasks import handle_video_data_file


class AssetViewSet(ModelViewSet):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer


class MissionViewSet(NestedViewSetMixin):
    queryset = Mission.objects.all()
    serializer_class = MissionSerializer
    parent_descriptor = ParentDescriptor(
        class_=Asset,
        pk_name='asset_pk',
        attr_name='asset'
    )


class FrameViewSet(NestedViewSetMixin):
    queryset = Frame.objects.all()
    serializer_class = FrameSerializer
    parent_descriptor = ParentDescriptor(
        class_=Mission,
        pk_name='mission_pk',
        attr_name='mission'
    )


class ObjectViewSet(NestedViewSetMixin):
    queryset = Object.objects.all()
    serializer_class = ObjectSerializer
    parent_descriptor = ParentDescriptor(
        class_=Frame,
        pk_name='frame_pk',
        attr_name='frame'
    )


class TelemetryViewSet(NestedViewSetMixin):
    queryset = Telemetry.objects.all()
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


class MissionDataViewSet(FileHandlerMixin):
    queryset = MissionData.objects.all()
    serializer_class = MissionDataSerializer
    parent_descriptor = ParentDescriptor(
        class_=Mission,
        pk_name='mission_pk',
        attr_name='mission'
    )
    file_handler = handle_mission_data_file


class VideoDataViewSet(FileHandlerMixin):
    queryset = VideoData.objects.all()
    serializer_class = VideoDataSerializer
    parent_descriptor = ParentDescriptor(
        class_=Mission,
        pk_name='mission_pk',
        attr_name='mission'
    )
    file_handler = handle_video_data_file
