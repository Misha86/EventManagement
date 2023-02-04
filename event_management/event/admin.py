"""Configuration for admin."""

from django.contrib import admin
from .models import Event, EventType


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    """Class for specifying EventType fields in admin."""

    model = EventType
    list_display = ('name', 'id')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """Class for specifying Event fields in admin."""

    model = EventType
    list_display = ('id', 'user', 'event_type', 'timestamp')
    list_filter = ('event_type', 'timestamp')
