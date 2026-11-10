from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_not_future(value):
    if value > timezone.localdate():
        raise ValidationError("You cannot log a habit for a future date.")
