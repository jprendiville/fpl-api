""" This module has a Django model to store details of an element type.

An element type is a goalkeeper, defender, midfielder or forward.
"""
from django.db import models

from common.models.event import Event
from fpl.enums.common_enums import ChipIdentifier
from utils.model_utils import BaseModel


class EventChipPlay(BaseModel):
    """ Class model to store an Event Chip Plays """

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="chip_plays"
    )
    chip_name = models.CharField(max_length=20, choices=ChipIdentifier.choices)
    num_played = models.IntegerField()


    def __str__(self):
        """ Return a formatted representation of an event status """
        return f"Chip {self.chip_name}"
