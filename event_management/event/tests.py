"""The module includes tests for models, serializers and views."""

from django.test import TestCase
from rest_framework.exceptions import ValidationError, ErrorDetail
from . import factories, serializers, models
from django.utils import timezone
from datetime import timedelta


class EvenModelTest(TestCase):
    """Class EvenModelTest for testing Event model."""

    def setUp(self):
        """This method adds needed info for tests."""
        self.e_factory = factories.EventFactory

    def test_create_event_valid_data(self):
        """Test for creating event with valid data."""
        user = factories.UserFactory()
        event_type = factories.EventTypeFactory()
        event = self.e_factory(user=user, event_type=event_type)

        self.assertIsNone(event.full_clean())
        self.assertEqual(event.user, user)
        self.assertEqual(event.event_type, event_type)
        self.assertGreater(event.timestamp, timezone.now())

    def test_create_event_timestamp_is_past(self):
        """Test for creating event with past timestamp."""
        with self.assertRaises(ValidationError) as ex:
            self.e_factory(timestamp=timezone.now() - timedelta(days=1)).full_clean()
        message = ex.exception.args[0]
        self.assertEqual(message, 'DateTime value should have future datetime.')

    def test_create_event_str_method(self):
        """Test for __str__ method."""
        event = self.e_factory()
        self.assertEqual(str(event), f'{event.__class__.__name__} #{event.id}')


class EvenSerializerTest(TestCase):
    """Class EvenSerializerTest for testing Event serializer."""

    def setUp(self):
        """This method adds needed info for tests."""
        self.user = factories.UserFactory()
        self.event_type = factories.EventTypeFactory()
        self.valid_data = {
            'event_type': self.event_type.name,
            'info': {},
            'timestamp': timezone.now() + timedelta(days=1),
        }
        self.serializer = serializers.EventSerializer(data=self.valid_data)

    def test_serialize_valid_data(self):
        """Check serializer with valid data."""
        self.serializer.is_valid(raise_exception=True)
        self.assertEqual(self.serializer.validated_data['event_type'].name, self.valid_data['event_type'])
        self.assertEqual(self.serializer.validated_data['timestamp'], self.valid_data['timestamp'])
        self.assertEqual(self.serializer.validated_data['info'], self.valid_data['info'])

        user = factories.UserFactory()
        event = self.serializer.save(user=user)
        self.assertEqual(event.user, user)
        self.assertEqual(event.event_type, self.event_type)

    def test_serialize_invalid_timestamp(self):
        """Check serializer with invalid timestamp."""
        self.valid_data.update(dict(timestamp=timezone.now() - timedelta(days=1)))
        with self.assertRaises(ValidationError) as ex:
            self.serializer.is_valid(raise_exception=True)

        message = ex.exception.args[0]
        self.assertEqual(
            message, {'timestamp': [ErrorDetail(string='DateTime value should have future datetime.', code='invalid')]}
        )

    def test_serialize_event_type_no_exist(self):
        """Check serializer when event type doesn't exist."""
        event_type = 'no such event type'
        self.valid_data.update(dict(event_type=event_type))

        self.assertFalse(models.EventType.objects.filter(name=event_type).exists())

        self.serializer.is_valid(raise_exception=True)
        self.serializer.save(user=self.user)

        self.assertEqual(self.serializer.data['event_type'], event_type)
        self.assertTrue(models.EventType.objects.filter(name=event_type).exists())

    def test_to_representation_method(self):
        """Check serializer a to_representation method."""
        self.serializer.is_valid(raise_exception=True)
        self.serializer.save(user=self.user)
        self.assertEqual(self.serializer.data["user"], self.user.username)
