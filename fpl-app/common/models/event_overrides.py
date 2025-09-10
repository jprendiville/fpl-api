""" This module has a Django model to store details of an element type.

An element type is a goalkeeper, defender, midfielder or forward.
"""
from django.db import models
from django.db.models import CASCADE

from common.models.event import Event
from players.models import ElementType
from utils.model_utils import BaseModel


class EventOverride(BaseModel):
    """ Class model to store an Event overrrides """

    gameweek = models.OneToOneField(Event, on_delete=CASCADE, primary_key=True)
    element_types = models.ManyToManyField(ElementType)
    pick_multiplier = models.IntegerField(null=True, blank=True)
    rules = models.JSONField(default=dict, blank=True)
    scoring = models.JSONField(default=dict, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        """ Return a formatted representation of an event status """
        return f"Gameweek {self.gameweek}"


    def full_clean(self, exclude=None, validate_unique=True):
        exclude = exclude or []
        exclude.extend(['gameweek', 'last_updated'])
        super().full_clean(exclude=exclude, validate_unique=validate_unique)

    class Meta:
        """ Meta class for uniqueness """
        constraints = [
            models.UniqueConstraint(
                fields=['gameweek'],
                name='unique_event_override'
            )
        ]