"""The module includes tests for models, serializers and views."""

from django.test import TestCase
from rest_framework.exceptions import ValidationError
from . import factories
from django.utils import timezone
from django.db.utils import IntegrityError
from datetime import timedelta


class EvenModelTest(TestCase):
    """Class EvenModelTest for testing Event model."""

    def test_create_event_valid_data(self):
        """Test for creating event with valid data."""
        event = factories.EventFactory()
        self.assertIsNone(event.full_clean())
        self.assertEqual(event.user.id, 1)
        self.assertEqual(event.event_type.id, 1)
        self.assertGreater(event.timestamp, timezone.now())

    def test_create_event_event_type_none(self):
        """Test for creating event without event_type."""
        with self.assertRaises(IntegrityError):
            factories.EventFactory(event_type=None)

    def test_create_event_user_none(self):
        """Test for creating event without event_type."""
        with self.assertRaises(IntegrityError):
            factories.EventFactory(user=None)

    def test_create_event_timestamp_is_past(self):
        """Test for creating event with past timestamp."""
        with self.assertRaises(ValidationError) as ex:
            factories.EventFactory(timestamp=timezone.now() - timedelta(days=1)).full_clean()
        message = ex.exception.args[0]
        self.assertEqual(message, 'DateTime value should have future datetime.')
