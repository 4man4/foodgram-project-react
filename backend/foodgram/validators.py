import re

from rest_framework.exceptions import ValidationError


def validate_positive_small_integer(value):
    if not (0 <= value <= 32767):
        raise ValidationError(
            'Укажите значение в диапазоне от 0 до 32767.'
        )
    return value


def validate_hex_color(value):
    match = re.search('^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', value)
    if not match:
        raise ValidationError('Введите цвет в HEX формате (#******).')
    return value
