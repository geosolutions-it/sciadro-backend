import traceback

from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.utils.translation import gettext as _
from rest_framework import status
from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from rest_framework.response import Response

import logging

logger = logging.getLogger('exception')


class BadRequestError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST


class BadFileFormatException(BadRequestError):
    pass


class FileManagementException(APIException):
    pass


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    tb = traceback.format_exc()
    logger.error(tb)
    if isinstance(exc, ObjectDoesNotExist) or isinstance(exc, Http404):
        response = Response(status=status.HTTP_400_BAD_REQUEST)
        response.data = {'details': str(exc), 'id': context.get('kwargs', {}).get('pk')}
    if response is not None:
        response.data['status_code'] = response.status_code
    else:
        response = Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        response.data = {'details': _('Something goes wrong. Contact technical support')}
    return response
