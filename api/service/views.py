from collections import OrderedDict

from django.contrib.gis.geos import LineString
from django.http import HttpResponse
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from django.utils.translation import gettext as _

from service.tasks import convert_avi_to_mp4, TASK_ENUM
from service.utils.asset import parse_asset_data
from service.utils.exception import BadRequestError, BadFileFormatException
from service.utils.storage_handler import SystemFileStorage
from service.utils.telemetry import parse_telemetry_data
from .models import Asset, TelemetryPosition, MissionVideo
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


class ResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('items', self.page.paginator.count),
            ('page_size', self.page_size),
            ('current_page', self.page.number),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))


class AssetViewSet(ModelViewSet):
    queryset = Asset.objects.all().order_by('pk')
    serializer_class = AssetSerializer
    pagination_class = ResultsSetPagination

    def list(self, request, *args, **kwargs):
        page = self.paginate_queryset(self.queryset)
        if page:
            return self.get_paginated_response(self.serializer_class(page, many=True).data)
        return Response(self.serializer_class(self.queryset,
                                              many=True).data)


class MissionViewSet(ModelViewSet):
    queryset = Mission.objects.all()
    serializer_class = MissionSerializer
    pagination_class = ResultsSetPagination

    def list(self, request, *args, **kwargs):
        filtered_qs = self.queryset.filter(asset=self.kwargs.get('asset_uuid')).order_by('pk')
        page = self.paginate_queryset(filtered_qs)
        if page:
            return self.get_paginated_response(self.serializer_class(page, many=True).data)
        return Response(self.serializer_class(filtered_qs,
                                              many=True).data)

    def retrieve(self, request, *args, **kwargs):
        return Response(
            self.serializer_class(
                self.queryset.get(pk=self.kwargs.get('pk'))
            ).data
        )

    def create(self, request, *args, **kwargs):
        file_type = 'application/zip'
        file = self.request.FILES.get('mission_file.mission_file')
        if file.content_type != file_type:
            raise BadFileFormatException(_('Only zip file is allowed'))

        file_name = file.name
        temporary_file_location = os.path.join(settings.MEDIA_ROOT, self.kwargs.get('asset_uuid'), file_name)
        storage_manager = SystemFileStorage(file_name, temporary_file_location)
        storage_manager.save_temporary_file(file)
        storage_manager.unzip_file()
        m = Mission()
        m.asset_id = self.kwargs.get('asset_uuid')
        m.name = request.POST.get('name')
        m.description = request.POST.get('description')
        m.note = request.POST.get('note')
        m.save()
        video_file = storage_manager.get_video_file()
        mission_file = MissionVideo()
        mission_geometry = []

        with storage_manager.get_telem_file() as telem:
            telemetry = parse_telemetry_data(telem)
            for telem_attribute in telemetry.attributes:
                values = telem_attribute.__dict__
                values.update({'mission': m})
                TelemetryAttribute.objects.create(**values)

            for telem_pos in telemetry.positions:
                values = telem_pos.__dict__
                values.update({'mission': m})
                mission_geometry.append((telem_pos.longitude, telem_pos.latitude))
                TelemetryPosition.objects.create(**values)
        m.geometry = LineString(mission_geometry)
        set_frame = True
        with storage_manager.get_xml_file() as xml:
            for frame in parse_asset_data(xml).frames:
                if set_frame:
                    mission_file.width = frame.size.width
                    mission_file.height = frame.size.height
                    set_frame = False
                frame.create_db_entity(m)

        mission_file.mission_file.save(video_file.name.split('/')[-1], video_file)
        m.mission_file = mission_file
        m.save()
        storage_manager.delete_temporary_files()
        convert_task = convert_avi_to_mp4.delay(m.id)
        return Response({
            'created': MissionSerializer(m).data,
            'task': {
                'type': TASK_ENUM.CONVERSION.value,
                'task_uuid': convert_task.id
            }
        })


class VideoStreamView(GenericViewSet, ListModelMixin):
    queryset = Mission.objects.all()

    def list(self, request, *args, **kwargs):
        m = self.queryset.get(id=self.kwargs.get('mission_uuid'))
        with m.mission_file.mission_file.open('rb') as mission_file:
            response = HttpResponse(mission_file.read(), content_type='video/mp4')
            response['Content-Disposition'] = f'inline; filename={m.mission_file.mission_file.name}'
            return response


class FrameViewSet(GenericViewSet, RetrieveModelMixin, ListModelMixin):
    queryset = Frame.objects.all()
    serializer_class = FrameSerializer
    pagination_class = ResultsSetPagination

    def list(self, request, *args, **kwargs):
        filtered_qs = self.queryset.filter(
            mission=self.kwargs.get('mission_uuid'),
            mission__asset=self.kwargs.get('asset_uuid')
        ).order_by('pk')
        page = self.paginate_queryset(filtered_qs)
        if page:
            return self.get_paginated_response(self.serializer_class(page, many=True).data)
        return Response(self.serializer_class(filtered_qs,
                                              many=True).data)

    def retrieve(self, request, *args, **kwargs):
        return Response(
            FrameSerializer(
                self.queryset.get(pk=self.kwargs.get('pk'))
            ).data
        )


class TelemetryViewSet(GenericViewSet, RetrieveModelMixin, ListModelMixin):
    pagination_class = ResultsSetPagination

    def get_queryset(self):
        telemetry_att = TelemetryAttribute.objects.filter(
            mission=self.kwargs.get('mission_uuid'),
            mission__asset=self.kwargs.get('asset_uuid')).order_by('pk')
        telemetry_pos = TelemetryPosition.objects.filter(
            mission=self.kwargs.get('mission_uuid'),
            mission__asset=self.kwargs.get('asset_uuid')
        ).order_by('pk')
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
    serializer_class = AnomalySerializer
    pagination_class = ResultsSetPagination

    def list(self, request, *args, **kwargs):
        filtered_qs = self.queryset.filter(
            frame=self.kwargs.get('frame_uuid'),
            frame__mission=self.kwargs.get('mission_uuid'),
            frame__mission__asset=self.kwargs.get('asset_uuid')
        ).order_by('pk')
        page = self.paginate_queryset(filtered_qs)
        if page:
            return self.get_paginated_response(self.serializer_class(page, many=True).data)
        return Response(self.serializer_class(filtered_qs,
                                              many=True).data)

    def retrieve(self, request, *args, **kwargs):
        return Response(
            AnomalySerializer(
                self.queryset.get(pk=self.kwargs.get('pk'))
            ).data
        )


class AnomalyPerMissionViewSet(GenericViewSet, ListModelMixin):
    queryset = Anomaly.objects.all()
    serializer_class = AnomalySerializer
    pagination_class = ResultsSetPagination

    def list(self, request, *args, **kwargs):
        filtered_qs = self.queryset.filter(
            frame__mission=self.kwargs.get('mission_uuid'),
            frame__mission__asset=self.kwargs.get('asset_uuid')
        ).order_by('pk')
        page = self.paginate_queryset(filtered_qs)
        if page:
            return self.get_paginated_response(self.serializer_class(page, many=True).data)
        return Response(self.serializer_class(filtered_qs,
                                              many=True).data)
