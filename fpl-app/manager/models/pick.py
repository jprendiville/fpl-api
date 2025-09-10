""" This module is a Django Model to store details about manager picks.

It has details like the manager (ForeignKey to ManagerTeam), player (ForeignKey
to Player), gameweek, position, is the captain/vice caption etc.
"""

from django.db import models
from django.db.models import CASCADE

from manager.models import ManagerTeam
from players.models import ElementType, Player
from utils.model_utils import BaseModel


class Pick(BaseModel):
    """ Class to store Pick details """

    gameweek = models.IntegerField(null=True)
    element = models.IntegerField(null=True)
    element_type = models.IntegerField(null=True)
    position = models.IntegerField(null=True)
    multiplier = models.IntegerField(null=True)
    is_captain = models.BooleanField(default=False)
    is_vice_captain = models.BooleanField(default=False)
    player = models.ForeignKey(Player, on_delete=CASCADE, null=True)
    player_type = models.ForeignKey(ElementType, on_delete=CASCADE, null=True)
    manager = models.ForeignKey(ManagerTeam, on_delete=CASCADE, null=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        """ Return a formatted representation of a pick """
        return f"{self.position}: " \
               f"{self.player.player_type.singular_name_short} " \
               f"{self.player.web_name} - {self.player.player_team.short_name}"

    def player_name(self):
        """ Return full player name, denoting if they are a captain """
        return f"{self.player.web_name} {'(C)' if self.is_captain else ''}"

    def shortened_player_name(self):
        """ Return shortened player name, denoting if they are a captain """
        return f"{self.player.shortened_name()} {'(C)' if self.is_captain else ''}"

    def expected_points(self):
        """ Return the expected points, accounting for if they are a captain """
        return self.player.ep_next * self.multiplier

    def format_expected_points(self):
        """ Return a formatted expected points, accounting for if they are a captain """
        return f"{self.player.ep_next * (self.multiplier if self.multiplier > 0 else 1)}"

    def is_sub(self):
        """ If they are a sub, set the multiplier to 0 as they won't get points """
        return self.multiplier == 0

    def get_live_points(self, gameweek):
        return self.player.get_player_live_points(gameweek) * self.multiplier

    def full_clean(self, exclude=None, validate_unique=True):
        exclude = exclude or []
        exclude.extend(['player', 'manager', 'player_type'])
        super().full_clean(exclude=exclude, validate_unique=validate_unique)

    class Meta:
        """ Meta class for uniqueness """
        constraints = [
            models.UniqueConstraint(
                fields=['manager', 'gameweek', 'player'],
                name='unique_manager_pick'
            )
        ]
        ordering = ('position',)
