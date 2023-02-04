"""The module includes project serializers."""

from .models import Event, EventType
from rest_framework import serializers


class EventTypeSerializer(serializers.ModelSerializer):
    """Serializer for EventType Model."""

    class Meta:
        """Class with a model and model fields for serialization."""

        model = EventType
        fields = ['name']
