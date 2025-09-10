""" This module has a Django model to store details of a player status.

Examples are Available, Injured, Doubtful, Suspended, Unavailable
"""

from django.db import models
from utils.model_utils import BaseModel


class PlayerStatus(BaseModel):
    """ Class model to store a Element Type (ie, goalkeeper, defender,
    midfielder, forward) """

    status = models.CharField(max_length=1, blank=True)
    description = models.CharField(max_length=32, blank=True)
    can_play = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        """ Return a formatted representation of an element type """
        return f"{self.status} ({self.description})"

    def full_clean(self, exclude=None, validate_unique=True):
        exclude = exclude or []
        super().full_clean(exclude=exclude, validate_unique=validate_unique)

    class Meta:
        """ Meta class for uniqueness """

        constraints = [
            models.UniqueConstraint(
                fields=['id', 'status'],
                name='unique_player_status'
            )
        ]