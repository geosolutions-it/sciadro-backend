from django.conf.urls import url
from django.urls import path
from django.urls import include

from service.celery_views import VideoConversionStatus
from .views import AssetViewSet, VideoStreamView, FrameViewSet, TelemetryViewSet, AnomalyViewSet, \
    AnomalyPerMissionViewSet
from .views import MissionViewSet
from rest_framework_nested.routers import DefaultRouter
from rest_framework_swagger.views import get_swagger_view



router = DefaultRouter()
router.register('assets', AssetViewSet, basename='assets')
router.register(r'assets/(?P<asset_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/missions', MissionViewSet, basename='missions')
router.register(r'assets/(?P<asset_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/missions/(?P<mission_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/video', VideoStreamView, basename='video')
router.register(r'assets/(?P<asset_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/missions/(?P<mission_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/telemetry',TelemetryViewSet , basename='telemetry')
router.register(r'assets/(?P<asset_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/missions/(?P<mission_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/frames', FrameViewSet, basename='frame')
router.register(r'assets/(?P<asset_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/missions/(?P<mission_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/anomalies', AnomalyPerMissionViewSet, basename='mission_anomalies')
router.register(r'assets/(?P<asset_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/missions/(?P<mission_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/frames/(?P<frame_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/anomalies', AnomalyViewSet, basename='anomaly')



schema_view = get_swagger_view(title='SCIADRO API')


urlpatterns = [
    path('', include(router.urls)),
    url(r'swagger', schema_view),
    path('celery/status/<uuid:task_id>', VideoConversionStatus.as_view())
]
