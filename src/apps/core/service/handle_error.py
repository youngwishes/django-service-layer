from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

from apps.core.service import BaseServiceError


def service_exception_handler(exc, context):
    if isinstance(exc, BaseServiceError):
        return Response(
            data={
                "error": exc.message,
                "detail": dict(**exc.context),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    return exception_handler(exc, context)
