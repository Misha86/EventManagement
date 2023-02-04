"""Module for all factories classes used in the tests."""

import factory
from . import models
from django.contrib.auth.hashers import make_password
from datetime import timedelta
import factory.fuzzy
from django.utils import timezone


def get_future_datetime(start=1, end=10, force_hour=13, force_minute=30):
    """Generate future datetime in the range start and end."""
    return factory.fuzzy.FuzzyDateTime(
        timezone.localtime(timezone.now()) + timedelta(days=start),
        timezone.localtime(timezone.now()) + timedelta(days=end),
        force_hour=force_hour,
        force_minute=force_minute,
        force_second=0,
        force_microsecond=0,
    )


class UserFactory(factory.django.DjangoModelFactory):
    """Factory class for creating users."""

    class Meta:
        """Class Meta for the definition of the User model."""

        model = models.User
        django_get_or_create = ("username",)

    username = factory.Sequence(lambda n: f"username_{n}")
    password = make_password('0987654321')


class EventTypeFactory(factory.django.DjangoModelFactory):
    """Factory class for creating event types."""

    class Meta:
        """Class Meta for the definition of the EventType model."""

        model = models.EventType
        django_get_or_create = ("name",)

    name = factory.Sequence(lambda n: f"username_{n}")


class EventFactory(factory.django.DjangoModelFactory):
    """Factory class for creating event."""

    class Meta:
        """Class Meta for the definition of the Event model."""

        model = models.Event

    user = factory.SubFactory(UserFactory)
    event_type = factory.SubFactory(EventTypeFactory)
    info = factory.LazyAttribute(lambda o: {'username': str(o.user)})
    timestamp = get_future_datetime()
