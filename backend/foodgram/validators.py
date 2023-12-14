import re

from rest_framework import status
from rest_framework.serializers import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import Follow


def custom_exception(exc):
    if isinstance(exc, ValidationError):
        return Response(
            {'errors': exc.detail['errors'][0]},
            status=status.HTTP_400_BAD_REQUEST
        )
    return APIView.handle_exception(exc)


def validate_subscriptions(serializer):
    request = serializer.context.get('request')
    user = serializer.context.get('user')
    author = serializer.context.get('author')
    if (
            request.method == 'POST'
            and Follow.objects.filter(user=user, author=author).exists()
    ):
        raise ValidationError({'errors': 'Вы уже подписаны.'})
    if (
            request.method == 'POST'
            and user.pk == author.pk
    ):
        raise ValidationError({'errors': 'Невозможно подписаться на себя.'})
    if (request.method == 'DELETE'
            and not Follow.objects.filter(user=user, author=author).exists()):
        raise ValidationError({'errors': 'Вы не подписаны.'})
    return serializer.context


def validate_positive_small_integer(value):
    if not (0 <= value <= 32767):
        raise ValidationError(
            'Укажите значение в диапазоне от 0 до 32767 минут.'
        )


def validate_hex_color(value):
    match = re.search('^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', value)
    if not match:
        raise ValidationError('Введите цвет в HEX формате (#******).')
