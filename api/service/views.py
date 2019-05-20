from django.http import HttpResponse
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from service.utils.asset import parse_asset_data
from service.utils.exception import BadRequestError
from service.utils.storage_handler import SystemFileStorage
from service.utils.telemetry import parse_telemetry_data
from .models import Asset, TelemetryPosition
from .serializers import AssetSerializer, TelemetryPositionSerializer
from .models import Mission
from .serializers import MissionSerializer
from .models import Frame
from .serializers import FrameSerializer
from .models import Anomaly
from .serializers import AnomalySerializer
from .models import TelemetryAttribute
from .serializers import TelemetrySerializer

from django.conf import settings
import os


class AssetViewSet(ModelViewSet):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer


class MissionViewSet(ModelViewSet):
    queryset = Mission.objects.all()
    serializer_class = MissionSerializer

    def list(self, request, *args, **kwargs):
        raise BadRequestError("TEST")
        return Response(self.serializer_class(self.queryset.filter(asset=self.kwargs.get('asset_uuid')), many=True).data)

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
        return Response(MissionSerializer(m).data)


class VideoStreamView(GenericViewSet, ListModelMixin):
    queryset = Mission.objects.all()

    def list(self, request, *args, **kwargs):
        m = self.queryset.get(id=self.kwargs.get('mission_uuid'))
        with m.video_file.open('rb') as video_file:
            response = HttpResponse(video_file.read(), content_type='video/avi')
            response['Content-Disposition'] = f'inline; filename={m.video_file.name}'
            return response


class FrameViewSet(GenericViewSet, RetrieveModelMixin, ListModelMixin):
    queryset = Frame.objects.all()

    def list(self, request, *args, **kwargs):
        return Response(FrameSerializer(self.queryset.filter(
            mission=self.kwargs.get('mission_uuid'),
            mission__asset=self.kwargs.get('asset_uuid')
        ), many=True).data)

    def retrieve(self, request, *args, **kwargs):
        return Response(
            FrameSerializer(
                self.queryset.get(pk=self.kwargs.get('pk'))
            ).data
        )


class TelemetryViewSet(GenericViewSet, RetrieveModelMixin, ListModelMixin):

    def get_queryset(self):
        telemetry_att = TelemetryAttribute.objects.filter(
            mission=self.kwargs.get('mission_uuid'),
            mission__asset=self.kwargs.get('asset_uuid'))
        telemetry_pos = TelemetryPosition.objects.filter(
            mission=self.kwargs.get('mission_uuid'),
            mission__asset=self.kwargs.get('asset_uuid')
        )
        return telemetry_att, telemetry_pos

    def list(self, request, *args, **kwargs):
        telem_att, telem_pos = self.get_queryset()
        return Response({
            'telemetry_attributes': TelemetrySerializer(telem_att, many=True).data,
            'telemetry_positions': TelemetryPositionSerializer(telem_pos, many=True).data
        })

    def retrieve(self, request, *args, **kwargs):
        telem_type = self.request.query_params.get('type')
        if telem_type == 'pos':
            return Response(
                TelemetryPositionSerializer(
                    TelemetryPosition.objects.get(pk=self.kwargs.get('pk'))
                ).data
            )
        elif telem_type == 'att':
            return Response(
                TelemetrySerializer(
                    TelemetryAttribute.objects.get(pk=self.kwargs.get('pk'))
                ).data
            )
        raise BadRequestError('Telemetry type is required')



class AnomalyViewSet(GenericViewSet, RetrieveModelMixin, ListModelMixin):
    queryset = Anomaly.objects.all()

    def list(self, request, *args, **kwargs):
        return Response(AnomalySerializer(self.queryset.filter(
            frame=self.kwargs.get('frame_uuid'),
            frame__mission=self.kwargs.get('mission_uuid'),
            frame__mission__asset=self.kwargs.get('asset_uuid')
        ), many=True).data)

    def retrieve(self, request, *args, **kwargs):
        return Response(
            AnomalySerializer(
                self.queryset.get(pk=self.kwargs.get('pk'))
            ).data
        )
