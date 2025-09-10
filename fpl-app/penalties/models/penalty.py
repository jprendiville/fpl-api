""" This module is a Django Model to store details about penalties.

It has details like the player, team, goalkeeper, gameweek and the result of
the penalty
"""

from django.db import models
from django.db.models import CASCADE
from django.utils.translation import gettext_lazy as _

from players.models import Event, Player
from teams.models import Team
from utils.model_utils import BaseModel


class Penalty(BaseModel):
    """ Class to store Penalty details """

    class Venue(models.TextChoices):
        """ Class to define Text Choices for the venue for a penalty """

        HOME = 'HOME', 'Home'
        AWAY = 'AWAY', 'Away'

    class Result(models.TextChoices):
        """ Class to define Text Choices for the result of a penalty """

        SCORED = 'SCORED', _('Scored')
        MISSED = 'MISSED', _('Missed')
        SAVED = 'SAVED', _('Saved')

    id = models.IntegerField(primary_key=True)
    team = models.ForeignKey(Team, on_delete=CASCADE, null=False)
    taker = models.ForeignKey(Player, related_name='player_taker',
                              on_delete=CASCADE, null=False)
    goalkeeper = models.ForeignKey(Player, related_name='player_goalkeeper',
                                   limit_choices_to={'player_type': 1},
                                   on_delete=CASCADE, null=False)
    gameweek = models.ForeignKey(Event, on_delete=CASCADE, null=False)
    venue = models.CharField(max_length=4,
                             choices=Venue.choices,
                             default=Venue.HOME)
    result = models.CharField(max_length=6,
                              choices=Result.choices,
                              default=Result.SCORED)
    var_awarded = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        """ Return a formatted representation of a penalty """
        return f"{self.taker} v {self.goalkeeper}: {self.result}"

    def full_clean(self, exclude=None, validate_unique=True):
        exclude = exclude or []
        super().full_clean(exclude=exclude, validate_unique=validate_unique)

    class Meta:
        """ Meta class for uniqueness """

        constraints = [
            models.UniqueConstraint(
                fields=['id'],
                name='unique_penalty'
            )
        ]
