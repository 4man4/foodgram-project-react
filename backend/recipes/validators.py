from django.core.exceptions import ValidationError
import re


def validate_positive_small_integer(value):
    if not (0 <= value <= 32767):
        raise ValidationError(
            'Укажите значение в диапазоне от 0 до 32767 минут.'
        )

def validate_hex_color(value):
    match = re.search('^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', value)
    if not match:
        raise ValidationError(
            'Введите цвет в HEX формате (#******).'
        )