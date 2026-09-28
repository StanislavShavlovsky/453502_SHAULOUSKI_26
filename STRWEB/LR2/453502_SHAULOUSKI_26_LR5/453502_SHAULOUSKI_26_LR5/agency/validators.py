import re
from datetime import date
from django.core.exceptions import ValidationError


def validate_by_phone_format(value):
    """
    Validates that the phone number strictly follows the Belarusian format: +375 (XX) XXX-XX-XX
    """
    if not re.match(r'^\+375 \((29|25|33|44)\) \d{3}-\d{2}-\d{2}$', value):
        raise ValidationError("Номер телефона должен строго соответствовать формату +375 (29) XXX-XX-XX")


def validate_adult_age(value):
    """
    Validates that the user's age based on their birthdate is at least 18 years old.
    """
    today = date.today()
    age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
    if age < 18:
        raise ValidationError("Регистрация разрешена только для лиц старше 18 лет.")