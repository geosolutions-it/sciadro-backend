import re
import mimetypes
import os

from collections import OrderedDict
from django.contrib.gis.geos import LineString
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from django.utils.translation import gettext as _
from wsgiref.util import FileWrapper
from django.http.response import StreamingHttpResponse
from service.file_streaming_wrapper import RangeFileWrapper
from service.tasks import convert_avi_to_mp4, TASK_ENUM
from service.utils.asset import parse_asset_data
from service.utils.exception import BadRequestError, BadFileFormatException
from service.utils.storage_handler import SystemFileStorage
from service.utils.telemetry import parse_telemetry_data
from .models import Asset, TelemetryPosition, MissionVideo
from .serializers import AssetSerializer, TelemetryPositionSerializer, MissionNarrowSerializer
from .models import Mission
from .serializers import MissionSerializer
from .models import Frame
from .serializers import FrameSerializer
from .models import Anomaly
from .serializers import AnomalySerializer
from .models import TelemetryAttribute
from .serializers import TelemetrySerializer
from django.conf import settings


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


def set_page_size(request, model_view_set):
    page_size = request.query_params.get(ResultsSetPagination.page_size_query_param)
    if page_size:
        model_view_set.pagination_class.page_size = int(page_size)
    else:
        model_view_set.pagination_class.page_size = 10


class AssetViewSet(ModelViewSet):
    queryset = Asset.objects.all().order_by('pk')
    serializer_class = AssetSerializer
    pagination_class = ResultsSetPagination

    def list(self, request, *args, **kwargs):
        set_page_size(request, self)
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
        set_page_size(request, self)
        filtered_qs = self.queryset.filter(asset=self.kwargs.get('asset_uuid')).order_by('pk')
        page = self.paginate_queryset(filtered_qs)
        if page:
            return self.get_paginated_response(MissionNarrowSerializer(page, many=True).data)
        return Response(MissionNarrowSerializer(filtered_qs,
                                                many=True).data)

    def retrieve(self, request, *args, **kwargs):
        return Response(
            self.serializer_class(
                self.queryset.get(pk=self.kwargs.get('pk')), context={'request': request}
            ).data
        )

    def create(self, request, *args, **kwargs):
        file_type = ['application/zip', 'application/x-zip', 'application/x-zip-compressed', 'application/octet-stream', 'application/x-compress','application/x-compressed', 'multipart/x-zip']
        file = self.request.FILES.get('mission_file.mission_file')
        if file.content_type not in file_type:
            raise BadFileFormatException(_('Only application/x-zip, application/x-zip-compressed, application/octet-stream, application/x-compress, application/x-compressed and multipart/x-zip mime type are allowed'))

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
            'created': MissionNarrowSerializer(m).data,
            'task': {
                'type': TASK_ENUM.CONVERSION.value,
                'task_uuid': convert_task.id
            }
        })


class VideoStreamView(GenericViewSet, ListModelMixin):
    queryset = Mission.objects.all()

    def list(self, request, *args, **kwargs):
        range_re = re.compile(r'bytes\s*=\s*(\d+)\s*-\s*(\d*)', re.I)
        m = self.queryset.get(id=self.kwargs.get('mission_uuid'))
        range_header = request.META.get('HTTP_RANGE', '').strip()
        range_match = range_re.match(range_header)
        file_path = m.mission_file.mission_file.path
        size = os.path.getsize(file_path)
        content_type = mimetypes.guess_type(file_path)[0]

        if range_match:
            first_byte, last_byte = range_match.groups()
            first_byte = int(first_byte) if first_byte else 0
            last_byte = int(last_byte) if last_byte else size - 1
            if last_byte >= size:
                last_byte = size - 1
            length = last_byte - first_byte + 1

            resp = StreamingHttpResponse(RangeFileWrapper(open(file_path, 'rb'), offset=first_byte, length=length),
                                         status=206, content_type=content_type)
            resp['Content-Length'] = str(length)
            resp['Content-Range'] = 'bytes %s-%s/%s' % (first_byte, last_byte, size)
        else:
            resp = StreamingHttpResponse(FileWrapper(open(file_path, 'rb')), content_type=content_type)
            resp['Content-Length'] = str(size)
        resp['Accept-Ranges'] = 'bytes'
        resp['Content-Disposition'] = f'inline; filename={m.mission_file.mission_file.name.split("/")[1]}'
        return resp


class FrameViewSet(GenericViewSet, RetrieveModelMixin, ListModelMixin):
    queryset = Frame.objects.all()
    serializer_class = FrameSerializer
    pagination_class = ResultsSetPagination

    def list(self, request, *args, **kwargs):
        set_page_size(request, self)
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
        set_page_size(request, self)
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
        set_page_size(request, self)
        filtered_qs = self.queryset.filter(
            frame__mission=self.kwargs.get('mission_uuid'),
            frame__mission__asset=self.kwargs.get('asset_uuid')
        ).order_by('pk')
        page = self.paginate_queryset(filtered_qs)
        if page:
            return self.get_paginated_response(self.serializer_class(page, many=True).data)
        return Response(self.serializer_class(filtered_qs,
                                              many=True).data)
