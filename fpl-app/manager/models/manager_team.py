""" This module is a Django Model to store some details about a Manager Team.

It's used to store if there is an Active Chip and last updated details (used
to determine whether to udpate the Manager details or not.
"""

from django.db import models

from manager.classes.league_standings import LeagueStandings
from utils.model_utils import BaseModel


class ManagerTeam(BaseModel):
    """ Class to store Manager Team details """

    active_chip = models.CharField(max_length=32, blank=True)
    last_updated_gameweek = models.IntegerField(null=True)
    last_update_timestamp = models.DateTimeField(null=True)

    def __str__(self):
        """ Return a formatted representation of a manager """
        return f"Manager is {self.id}"

    def display_active_chip(self):
        """ Display the chip description if it is active """
        return f" ({self.active_chip.upper()} ACTIVE!)" if self.active_chip != "" else ""

    def get_pick_live_points(self, gameweek):
        pick_live_points = 0
        for pick in self.pick_set.all():
            if pick.gameweek == gameweek.id:
                pick_live_points += pick.get_live_points(gameweek)
        return pick_live_points

    def get_gameweek_live_points(self, gameweek):
        return self.get_pick_live_points(gameweek)

    def get_total_live_points(self, gameweek, this_league):
        if LeagueStandings.bonus_added(gameweek):
            return this_league.total
        return this_league.total + self.get_gameweek_live_points(gameweek)

    def full_clean(self, exclude=None, validate_unique=True):
        exclude = exclude or []
        super().full_clean(exclude=exclude, validate_unique=validate_unique)

    class Meta:
        """ Meta class for uniqueness """
        constraints = [
            models.UniqueConstraint(
                fields=['id'],
                name='unique_manager_team'
            )
        ]