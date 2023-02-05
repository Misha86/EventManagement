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
        """Test for creating event with past timestamp (exception raises)."""
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

# class AppointmentViewTest(APITestCase):
#     """Class AppointmentViewTest for testing Appointment view."""
#
#     def setUp(self):
#         """This method adds needed info for tests."""
#         self.create_ap_url = "api:appointments-list-create"
#         specialist = SpecialistFactory(add_schedule=True)
#         location = LocationFactory()
#         fake_data = AppointmentFactory.build(specialist=specialist, location=location)
#         self.valid_data = {
#             "start_time": fake_data.start_time,
#             "specialist": fake_data.specialist.id,
#             "location": fake_data.location.id,
#             "duration": fake_data.duration,
#             "customer_firstname": fake_data.customer_lastname,
#             "customer_lastname": fake_data.customer_lastname,
#             "customer_email": fake_data.customer_email,
#         }
#
#     def tearDown(self):
#         """This method deletes all users and cleans avatars' data."""
#         CustomUser.objects.all().delete()
#
#     def test_get_all_appointments(self):
#         """Test for getting all appointments."""
#         AppointmentFactory.create_batch(5)
#         response = self.client.get(reverse(self.create_ap_url), format="json")
#         results = response.data["results"]
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(results), 5)
#
#     def test_create_appointment_by_specialist_fail(self):
#         """Test for creating appointment by specialist is forbidden."""
#         specialist = SpecialistFactory()
#         self.client.force_authenticate(specialist)
#
#         response = self.client.post(reverse(self.create_ap_url), self.valid_data, format="json")
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
#
#     def test_create_appointment_by_admin(self):
#         """Test for creating appointment by admin."""
#         admin = AdminFactory()
#         self.client.force_authenticate(admin)
#
#         response = self.client.post(reverse(self.create_ap_url), self.valid_data, format="json")
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#
#     def test_create_appointment_by_manager_fail(self):
#         """Test for creating appointment by manager is forbidden."""
#         manager = ManagerFactory()
#         self.client.force_authenticate(manager)
#
#         response = self.client.post(reverse(self.create_ap_url), self.valid_data, format="json")
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
#
#     def test_create_appointment_by_superuser(self):
#         """Test for creating appointment by superuser."""
#         superuser = SuperuserFactory()
#
#         self.client.force_authenticate(superuser)
#
#         response = self.client.post(reverse(self.create_ap_url), self.valid_data, format="json")
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#
#     def test_create_appointment_not_specialist_schedule_error(self):
#         """Create appointment for specialist without schedule."""
#         admin = AdminFactory()
#         specialist = SpecialistFactory()
#         self.client.force_authenticate(admin)
#         self.valid_data.update(dict(specialist=specialist.id))
#
#         response = self.client.post(reverse(self.create_ap_url), self.valid_data, format="json")
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

