from django.urls import path
from django.urls import include
from .views import AssetViewSet, VideoStreamView, FrameViewSet, TelemetryViewSet, AnomalyViewSet
from .views import MissionViewSet
from rest_framework_nested.routers import DefaultRouter



router = DefaultRouter()
router.register('assets', AssetViewSet, basename='assets')
router.register(r'assets/(?P<asset_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/missions', MissionViewSet, basename='missions')
router.register(r'assets/(?P<asset_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/missions/(?P<mission_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/video', VideoStreamView, basename='video')
router.register(r'assets/(?P<asset_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/missions/(?P<mission_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/telemetry',TelemetryViewSet , basename='frame')
router.register(r'assets/(?P<asset_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/missions/(?P<mission_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/frames', FrameViewSet, basename='telemetry')
router.register(r'assets/(?P<asset_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/missions/(?P<mission_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/frames/(?P<frame_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/anomalies', AnomalyViewSet, basename='anomaly')


urlpatterns = [
    path('', include(router.urls)),
]
