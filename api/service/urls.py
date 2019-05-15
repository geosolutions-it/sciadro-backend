from django.urls import path
from django.urls import include
from .views import AssetViewSet
from .views import MissionViewSet
from .views import FrameViewSet
from .views import ObjectViewSet
from .views import TelemetryViewSet
from rest_framework_nested.routers import DefaultRouter
from rest_framework_nested.routers import NestedSimpleRouter
# from .views import MissionDataViewSet
# from .views import VideoDataViewSet


router = DefaultRouter()
router.register('assets', AssetViewSet, basename='assets')
router.register(r'assets/(?P<asset_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/missions', MissionViewSet, basename='missions')

# asset_router = NestedSimpleRouter(router, 'assets', lookup='asset')
# asset_router.register('missions', MissionViewSet, basename='missions')

# mission_router = NestedSimpleRouter(asset_router, 'missions', lookup='mission')
# mission_router.register('frames', FrameViewSet, basename='frames')
# mission_router.register('telemetries', TelemetryViewSet, basename='telemetries')
#
# frame_router = NestedSimpleRouter(mission_router, 'frames', lookup='frame')
# frame_router.register('objects', ObjectViewSet, basename='objects')
#

urlpatterns = [
    path('', include(router.urls)),
    # path('', include(asset_router.urls)),
    # path('', include(mission_router.urls)),
    # path('', include(frame_router.urls))
]
