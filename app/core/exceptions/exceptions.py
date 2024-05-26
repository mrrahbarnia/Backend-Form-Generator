from django.core.exceptions import ValidationError as DjangoValidationError, PermissionDenied
from django.http import Http404

from rest_framework.views import exception_handler
from rest_framework import exceptions, status
from rest_framework.serializers import as_serializer_error


def custom_exception_handler(exc, ctx):
    """
    {
        "message": "Error message",
        "extra": {}
    }
    """
    if isinstance(exc, DjangoValidationError):
        exc = exceptions.ValidationError(as_serializer_error(exc=exc))
    
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    
    if isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()
    
    response = exception_handler(exc, ctx)

    if response is None:
        data = {
            "message": exc.default_code,
            "extra": {}
        }
        return response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    if isinstance(exc.detail, (list, dict)):
        response.data = {
            "detail": response.data
        }
    
    if isinstance(exc, exceptions.ValidationError):
        response.data["message"] = "Validation Error"
        response.data["extra"] = {
            "fields": response.data["detail"]
        }
    else:
        response.data["message"] = response.data["detail"]
        response.data["extra"] = {}
    
    del response.data["detail"]

    return response
