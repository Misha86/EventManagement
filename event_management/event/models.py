"""Module for all project models."""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
import uuid

User = get_user_model()


class EventType(models.Model):
    """This class represents a basic Event Type (for an event system).

    Attributes:
        name (str): Name of the event type
    """

    name = models.CharField(_("Name"), max_length=256, help_text=_('This field is required'))

    class Meta:
        """This meta class stores verbose names and ordering data."""

        ordering = ['id']
        verbose_name_plural = _('Event Types')

    def __str__(self) -> str:
        """str: Returns class name and instance id."""
        return f"{self.__class__.__name__} #{self.id}"


class Event(models.Model):
    """This class represents a basic Event (for an event system).

    Attributes:
        id (uuid4): Primary key type uuid4
        user (int): User id who creates event
        event_type (int): Represents event type id
        info (json): Some information about concrete event
        timestamp (datetime): Event time and date
        created_at (datetime): Time of creation of the event
    """

    help_texts = {'required': _('This field is required')}

    id = models.UUIDField('UUID', primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, related_name='events', on_delete=models.CASCADE, verbose_name=_('User'))
    event_type = models.ForeignKey(EventType, related_name='events', on_delete=models.CASCADE,
                                   verbose_name=_('Event Type'))
    info = models.JSONField(_('Event info'), help_text=help_texts['required'])
    timestamp = models.DateTimeField(_('Event datetime'), help_text=help_texts['required'])
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))

    class Meta:
        """This meta class stores verbose names and ordering data."""

        ordering = ['id']
        verbose_name_plural = _('Events')

    def __str__(self) -> str:
        """str: Returns class name and instance id."""
        return f"{self.__class__.__name__} #{self.id}"
