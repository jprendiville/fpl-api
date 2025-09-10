""" This module is a Django Model to store predicted points v actual points.

It is to be used to evaluate the machine learning
"""

from django.db import models
from django.db.models import CASCADE

from players.classes.gameresult import GameResult
from players.models import Event, Player
from common.models.season import Season
from teams.models.team import Team
from utils.model_utils import BaseModel


class PlayerPrediction(BaseModel):
    """ Class to store Player details """

    element = models.IntegerField(null=True)
    season = models.ForeignKey(Season, on_delete=CASCADE)
    total_points = models.IntegerField(null=True)
    prediction = models.DecimalField(decimal_places=2, max_digits=6, null=True)
    team_h_score = models.IntegerField(null=True)
    team_a_score = models.IntegerField(null=True)
    was_home = models.IntegerField(null=True)
    gameweek = models.ForeignKey(Event, on_delete=CASCADE)
    opponent = models.ForeignKey(Team, on_delete=CASCADE, null=True)
    player = models.ForeignKey(Player, on_delete=CASCADE)
    finished = models.BooleanField(default=False, null=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        """ Return a formatted representation of a player """
        return f"{self.player.web_name} ({self.player.player_team.short_name})"

    def home_or_away(self):
        """ Returns whether the game was Home or Away """
        return "(H)" if self.was_home == 1 else "(A)"

    def result(self):
        """ Returns a formatted string of the result of the game """
        return f"{abs(self.team_h_score)} - {abs(self.team_a_score)}" \
            if self.team_h_score is not None and \
               self.team_a_score is not None else ""

    def game_result(self):
        """ Return Win/Lost/Draw"""

        if self.team_h_score == self.team_a_score:
            return GameResult.DRAW

        if (self.was_home == 1 and (abs(self.team_h_score) >
                                    abs(self.team_a_score))) or \
                (self.was_home != 1 and (abs(self.team_a_score) >
                                         abs(self.team_h_score))):
            return GameResult.WIN

        return GameResult.LOSE


    def get_opponent(self):
        # Is this the home team?
        if self.was_home:
            return f"{self.opponent.name} (H)"
        # else, they're playing the opponent away
        return f"{self.opponent.name} (A)"


    def get_opponent_short(self):
        # Is this the home team?
        if self.was_home:
            return f"{self.opponent.short_name} (H)"
        # else, they're playing the opponent away
        return f"{self.opponent.short_name} (A)"


    def full_clean(self, exclude=None, validate_unique=True):
        exclude = exclude or []
        exclude.extend(['gameweek', 'opponent', 'player'])
        super().full_clean(exclude=exclude, validate_unique=validate_unique)

    class Meta:
        """ Meta class for uniqueness """

        constraints = [
            models.UniqueConstraint(
                fields=['element', 'gameweek'],
                name='unique_player_prediction'
            )
        ]
