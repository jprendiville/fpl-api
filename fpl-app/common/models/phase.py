""" This module is a Django Model to store details about Phases.

A phase is a grouping of gameweeks. The idea is that we can group gameweeks by
months on the year. The dilemma is that sometimes an event in a gameweek can
rollover to the next month. For this reason we can't use the actual month, but
this grouping solves the issue.
"""

from django.db import models
from utils.model_utils import BaseModel


class Phase(BaseModel):
    """ Class to store Phase details """

    name = models.CharField(max_length=10, blank=True)
    start_event = models.IntegerField(null=True)
    stop_event = models.IntegerField(null=True)
    highest_score =  models.IntegerField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        """ Return a formatted representation of a phase """
        return f"Phase {self.name}"

    def full_clean(self, exclude=None, validate_unique=True):
        exclude = exclude or []
        super().full_clean(exclude=exclude, validate_unique=validate_unique)

    class Meta:
        """ Meta class for uniqueness """

        constraints = [
            models.UniqueConstraint(
                fields=['id', 'name'],
                name='unique_phase'
            )
        ]