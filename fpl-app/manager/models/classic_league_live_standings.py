""" This module has a Django model to store details of a classic league live
standing.

It stores live points for players.
"""

from django.db import models
from django.db.models import CASCADE

from players.models import Player
from utils.model_utils import BaseModel


class ClassicLeagueLiveStandings(BaseModel):
    """ Class model to store a Classic League Standing """

    player = models.OneToOneField(Player, on_delete=CASCADE, unique=True, null=True)
    minutes = models.IntegerField(null=True)
    goals_scored = models.IntegerField(null=True)
    assists = models.IntegerField(null=True)
    clean_sheets = models.IntegerField(null=True)
    goals_conceded = models.IntegerField(null=True)
    own_goals = models.IntegerField(null=True)
    penalties_saved = models.IntegerField(null=True)
    penalties_missed = models.IntegerField(null=True)
    yellow_cards = models.IntegerField(null=True)
    red_cards = models.IntegerField(null=True)
    saves = models.IntegerField(null=True)
    bonus = models.IntegerField(null=True)
    bps = models.IntegerField(null=True)
    influence = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    creativity = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    threat = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    ict_index = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    starts = models.IntegerField(null=True)
    expected_goals = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    expected_assists = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    expected_goal_involvements = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    expected_goals_conceded = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    total_points = models.IntegerField(null=True)
    in_dreamteam = models.BooleanField(default=False)
    mng_win = models.IntegerField(null=True)
    mng_draw = models.IntegerField(null=True)
    mng_loss = models.IntegerField(null=True)
    mng_underdog_win = models.IntegerField(null=True)
    mng_underdog_draw = models.IntegerField(null=True)
    mng_clean_sheets = models.IntegerField(null=True)
    mng_goals_scored = models.IntegerField(null=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        """ Return a formatted representation of a players live standing """
        return f"{self.id.web_name} : {self.total_points} ({self.minutes} mins)"

    def full_clean(self, exclude=None, validate_unique=True):
        exclude = exclude or []
        exclude.extend(['player'])
        super().full_clean(exclude=exclude, validate_unique=validate_unique)

    class Meta:
        """ Meta class for uniqueness """
        constraints = [
            models.UniqueConstraint(
                fields=['player'],
                name='unique_classic_league_live_standings'
            )
        ]