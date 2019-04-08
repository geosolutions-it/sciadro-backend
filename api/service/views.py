from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
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
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse


@api_view(('GET',))
def api_root(request, format=None):
    return Response({
        'assets': reverse('asset-list', request=request, format=format),
        'missions': reverse('mission-list', request=request, format=format),
        'frames': reverse('frame-list', request=request, format=format),
        'objects': reverse('object-list', request=request, format=format),
        'telemetries': reverse('telemetry-list', request=request, format=format)
    })


class AssetList(ListCreateAPIView):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer


class AssetDetail(RetrieveUpdateDestroyAPIView):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer


class MissionList(ListCreateAPIView):
    queryset = Mission.objects.all()
    serializer_class = MissionSerializer


class MissionDetail(RetrieveUpdateDestroyAPIView):
    queryset = Mission.objects.all()
    serializer_class = MissionSerializer


class FrameList(ListCreateAPIView):
    queryset = Frame.objects.all()
    serializer_class = FrameSerializer


class FrameDetail(RetrieveUpdateDestroyAPIView):
    queryset = Frame.objects.all()
    serializer_class = FrameSerializer


class ObjectList(ListCreateAPIView):
    queryset = Object.objects.all()
    serializer_class = ObjectSerializer


class ObjectDetail(RetrieveUpdateDestroyAPIView):
    queryset = Object.objects.all()
    serializer_class = ObjectSerializer


class TelemetryList(ListCreateAPIView):
    queryset = Telemetry.objects.all()
    serializer_class = TelemetrySerializer


class TelemetryDetail(RetrieveUpdateDestroyAPIView):
    queryset = Telemetry.objects.all()
    serializer_class = TelemetrySerializer
