import re

from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


def custom_exception(exc):
    if isinstance(exc, ValidationError):
        return Response(
            {'errors': exc.detail['errors'][0]},
            status=status.HTTP_400_BAD_REQUEST
        )
    return APIView().handle_exception(exc)


def validate_positive_small_integer(value):
    if not (0 <= value <= 32767):
        raise ValidationError(
            'Укажите значение в диапазоне от 0 до 32767 минут.'
        )
    return value


def validate_hex_color(value):
    match = re.search('^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', value)
    if not match:
        raise ValidationError('Введите цвет в HEX формате (#******).')
    return value
