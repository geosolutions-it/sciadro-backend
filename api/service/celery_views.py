from uuid import UUID

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from service.tasks import convert_avi_to_mp4


class VideoConversionStatus(APIView):

    def get(self, request: Request, task_id: UUID) -> Response:
        return Response(convert_avi_to_mp4.AsyncResult(str(task_id)).state)
