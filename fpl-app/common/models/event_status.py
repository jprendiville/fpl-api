""" This module has a Django model to store details of an element type.

An element type is a goalkeeper, defender, midfielder or forward.
"""
from django.db import models
from django.db.models import CASCADE

from common.models.event import Event
from utils.model_utils import BaseModel


class EventStatus(BaseModel):
    """ Class model to store an Event status """

    bonus_added = models.BooleanField()
    date = models.DateField()
    event = models.IntegerField(null=True)
    points = models.CharField(max_length=1, blank=True)
    gameweek = models.ForeignKey(Event, on_delete=CASCADE, null=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        """ Return a formatted representation of an event status """
        return f"Gameweek {self.event}, Date {self.date}, Bonus added: {self.bonus_added}"


    def full_clean(self, exclude=None, validate_unique=True):
        exclude = exclude or []
        exclude.extend(['gameweek', 'last_updated'])
        super().full_clean(exclude=exclude, validate_unique=validate_unique)

    class Meta:
        """ Meta class for uniqueness """
        constraints = [
            models.UniqueConstraint(
                fields=['event', 'date'],
                name='unique_event_status'
            )
        ]