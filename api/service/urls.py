from django.urls import path
from .views import AssetList
from .views import AssetDetail
from .views import MissionList
from .views import MissionDetail
from .views import FrameList
from .views import FrameDetail
from .views import ObjectList
from .views import ObjectDetail
from .views import TelemetryList
from .views import TelemetryDetail
from .views import api_root


urlpatterns = [
    path('', api_root),
    path('assets/', AssetList.as_view(), name='asset-list'),
    path('assets/<int:pk>/', AssetDetail.as_view()),
    path('missions/', MissionList.as_view(), name='mission-list'),
    path('missions/<int:pk>/', MissionDetail.as_view()),
    path('frames/', FrameList.as_view(), name='frame-list'),
    path('frames/<int:pk>/', FrameDetail.as_view()),
    path('objects/', ObjectList.as_view(), name='object-list'),
    path('objects/<int:pk>/', ObjectDetail.as_view()),
    path('telemetries/', TelemetryList.as_view(), name='telemetry-list'),
    path('telemetries/<int:pk>/', TelemetryDetail.as_view())
]
