"""Validators for EventManagement project."""

from django.utils import timezone

from rest_framework.exceptions import ValidationError


def validate_datetime_is_future(value):
    """Datetime values should have future date."""
    if timezone.now() > value:
        raise ValidationError('DateTime value should have future datetime.')
