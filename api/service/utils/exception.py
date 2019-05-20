from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from rest_framework.response import Response


class BadRequestError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST


class FileManagementException(APIException):
    pass


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if isinstance(exc, ObjectDoesNotExist):
        response = Response(status=status.HTTP_400_BAD_REQUEST)
        response.data = {"details": str(exc)}
    if response is not None:
        response.data['status_code'] = response.status_code
    else:
        response = Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        response.data = {"details": str(exc)}
    return response
