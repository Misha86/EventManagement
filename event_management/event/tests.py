"""The module includes tests for models, serializers and views.

EvenModelTest (Class EvenModelTest for testing Event model):
 - Test for creating event with valid data;
 - Test for creating event with past timestamp (exception raises);
 - Test for __str__ method.

EvenSerializerTest (Class EvenSerializerTest for testing Event serializer):
 - Test for serializer with valid data;
 - Test for serializer with invalid timestamp;
 - Test for serializer when event type doesn't exist;
 - Test for serializer a to_representation method.

EvenViewTest (Class EvenViewTest for testing Event view):
 - Test for creating event (status code 201);
 - Test for creating event by not authenticated user (status code 401);
 - Test for creating event using GET method (status code 405);
 - Test for creating event with None some field (status code 400);
 - Test for creating event without data (status code 400).
"""

from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ErrorDetail, ValidationError
from rest_framework.test import APITestCase

from . import factories, models, serializers


class EvenModelTest(TestCase):
    """Class EvenModelTest for testing Event model."""

    def setUp(self):
        """Set needed info for tests."""
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
        """Test for creating event with past timestamp (exception raises)."""
        with self.assertRaises(ValidationError) as ex:
            self.e_factory(timestamp=timezone.now() - timedelta(days=1)).full_clean()
        message = ex.exception.args[0]
        self.assertEqual(message, "DateTime value should have future datetime.")

    def test_create_event_str_method(self):
        """Test for __str__ method."""
        event = self.e_factory()
        self.assertEqual(str(event), f"{event.__class__.__name__} #{event.id}")


class EvenSerializerTest(TestCase):
    """Class EvenSerializerTest for testing Event serializer."""

    def setUp(self):
        """Set needed info for tests."""
        self.user = factories.UserFactory()
        self.event_type = factories.EventTypeFactory()
        self.valid_data = {
            "event_type": self.event_type.name,
            "info": {},
            "timestamp": timezone.now() + timedelta(days=1),
        }
        self.serializer = serializers.EventSerializer(data=self.valid_data)

    def test_serialize_valid_data(self):
        """Test for serializer with valid data."""
        self.serializer.is_valid(raise_exception=True)
        self.assertEqual(self.serializer.validated_data["event_type"].name, self.valid_data["event_type"])
        self.assertEqual(self.serializer.validated_data["timestamp"], self.valid_data["timestamp"])
        self.assertEqual(self.serializer.validated_data["info"], self.valid_data["info"])

        user = factories.UserFactory()
        event = self.serializer.save(user=user)
        self.assertEqual(event.user, user)
        self.assertEqual(event.event_type, self.event_type)

    def test_serialize_invalid_timestamp(self):
        """Test for serializer with invalid timestamp."""
        self.valid_data.update(dict(timestamp=timezone.now() - timedelta(days=1)))
        with self.assertRaises(ValidationError) as ex:
            self.serializer.is_valid(raise_exception=True)

        message = ex.exception.args[0]
        self.assertEqual(
            message, {"timestamp": [ErrorDetail(string="DateTime value should have future datetime.", code="invalid")]}
        )

    def test_serialize_event_type_no_exist(self):
        """Test for serializer when event type doesn't exist."""
        event_type = "no such event type"
        self.valid_data.update(dict(event_type=event_type))

        self.assertFalse(models.EventType.objects.filter(name=event_type).exists())

        self.serializer.is_valid(raise_exception=True)
        self.serializer.save(user=self.user)

        self.assertEqual(self.serializer.data["event_type"], event_type)
        self.assertTrue(models.EventType.objects.filter(name=event_type).exists())

    def test_to_representation_method(self):
        """Test for serializer a to_representation method."""
        self.serializer.is_valid(raise_exception=True)
        self.serializer.save(user=self.user)
        self.assertEqual(self.serializer.data["user"], self.user.username)


class EvenViewTest(APITestCase):
    """Class EvenViewTest for testing Event view."""

    def setUp(self):
        """Set needed info for tests."""
        self.create_event_url = "event:create-event"
        self.event_type = factories.EventTypeFactory()
        self.event_data = factories.EventFactory.build()
        self.valid_data = {
            "event_type": self.event_type.name,
            "info": self.event_data.info,
            "timestamp": self.event_data.timestamp,
        }
        self.token = Token.objects.create(user=factories.UserFactory())
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_create_event(self):
        """Test for creating event (status code 201)."""
        response = self.client.post(reverse(self.create_event_url), self.valid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["event_type"], self.event_type.name)
        self.assertEqual(response.data["info"], self.event_data.info)
        self.assertEqual(response.data["timestamp"], self.event_data.timestamp.isoformat())

    def test_create_event_user_not_authenticated_error(self):
        """Test for creating event by not authenticated user (status code 401)."""
        self.client.credentials()
        response = self.client.post(reverse(self.create_event_url), self.valid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Authentication credentials were not provided.")

    def test_create_event_get_method_fail(self):
        """Test for creating event using GET method (status code 405)."""
        response = self.client.get(reverse(self.create_event_url), self.valid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(
            response.data["detail"], ErrorDetail(string='Method "GET" not allowed.', code="method_not_allowed")
        )

    def test_create_event_event_type_null_fail(self):
        """Test for creating event with None some field (status code 400)."""
        for field in ["event_type", "info", "timestamp"]:
            with self.subTest(field=field):
                response = self.client.post(
                    reverse(self.create_event_url), {**self.valid_data, **{field: None}}, format="json"
                )
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertEqual(
                    response.data, {field: [ErrorDetail(string="This field may not be null.", code="null")]}
                )

    def test_create_event_without_data_fail(self):
        """Test for creating event without data (status code 400)."""
        response = self.client.post(reverse(self.create_event_url), format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "event_type": [ErrorDetail(string="This field is required.", code="required")],
                "info": [ErrorDetail(string="This field is required.", code="required")],
                "timestamp": [ErrorDetail(string="This field is required.", code="required")],
            },
        )
