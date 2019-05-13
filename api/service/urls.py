from django.urls import path
from django.urls import include
from .views import AssetViewSet
from .views import MissionViewSet
from .views import FrameViewSet
from .views import ObjectViewSet
from .views import TelemetryViewSet
from rest_framework_nested.routers import DefaultRouter
from rest_framework_nested.routers import NestedSimpleRouter
# from .views import TelemetryDataViewSet
from .views import MissionDataViewSet
from .views import VideoDataViewSet


router = DefaultRouter()
router.register('assets', AssetViewSet, basename='assets')

asset_router = NestedSimpleRouter(router, 'assets', lookup='asset')
asset_router.register('missions', MissionViewSet, basename='missions')

mission_router = NestedSimpleRouter(asset_router, 'missions', lookup='mission')
mission_router.register('frames', FrameViewSet, basename='frames')
mission_router.register('telemetries', TelemetryViewSet, basename='telemetries')
# mission_router.register('telemetry_files', TelemetryDataViewSet, basename='telemetry_files')
mission_router.register('mission_files', MissionDataViewSet, basename='mission_files')
mission_router.register('video_files', VideoDataViewSet, basename='video_files')

frame_router = NestedSimpleRouter(mission_router, 'frames', lookup='frame')
frame_router.register('objects', ObjectViewSet, basename='objects')


urlpatterns = [
    path('', include(router.urls)),
    path('', include(asset_router.urls)),
    path('', include(mission_router.urls)),
    path('', include(frame_router.urls))
]
