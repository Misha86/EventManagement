"""The module includes project serializers."""

from .models import Event, EventType
from rest_framework import serializers


class EventTypeSerializer(serializers.ModelSerializer):
    """Serializer for EventType Model."""

    class Meta:
        """Class with a model and model fields for serialization."""

        model = EventType
        fields = ['name']


class EventSerializer(serializers.ModelSerializer):
    """Serializer for Event Model."""

    event_type = serializers.CharField(max_length=256, required=True)

    class Meta:
        """Class with a model and model fields for serialization."""

        model = Event
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at')

    def validate_event_type(self, name):
        """Get existing event type or create new."""

        event_type, _ = EventType.objects.get_or_create(name=name)
        return event_type
