""" This module is a Django Model to store details about player history.

It has details like player (ForeignKey to Player), opponent (ForeignKey to
Team), fixture, score, transfers etc
"""

from django.db import models
from django.db.models import CASCADE

from players.classes.gameresult import GameResult
from utils.date_utils import day_month_year_from_datetime
from utils.model_utils import BaseModel


class PlayerHistory(BaseModel):
    """ Class to store Player History details """

    # Composite key fields (using the constraint to make these composites unique)
    element = models.IntegerField(null=True)
    fixture = models.IntegerField(null=True)

    opponent_team = models.IntegerField(null=True)
    total_points = models.IntegerField(null=True)
    was_home = models.BooleanField(default=True)
    kickoff_time = models.DateTimeField(null=True)
    team_h_score = models.IntegerField(null=True, blank=True)
    team_a_score = models.IntegerField(null=True, blank=True)
    round = models.IntegerField(null=True)
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
    value = models.IntegerField(null=True)
    transfers_balance = models.IntegerField(null=True)
    selected = models.IntegerField(null=True)
    transfers_in = models.IntegerField(null=True)
    transfers_out = models.IntegerField(null=True)
    starts = models.IntegerField(null=True)
    expected_goals = models.DecimalField(max_digits=6,
                                         decimal_places=2,
                                         null=True)
    expected_assists = models.DecimalField(max_digits=6,
                                           decimal_places=2,
                                           null=True)
    expected_goal_involvements = models.DecimalField(max_digits=6,
                                                     decimal_places=2,
                                                     null=True)
    expected_goals_conceded = models.DecimalField(max_digits=6,
                                                  decimal_places=2,
                                                  null=True)
    modified = models.BooleanField(default=False)
    mng_win = models.IntegerField(null=True, blank=True)
    mng_draw = models.IntegerField(null=True, blank=True)
    mng_loss = models.IntegerField(null=True, blank=True)
    mng_underdog_win = models.IntegerField(null=True, blank=True)
    mng_underdog_draw = models.IntegerField(null=True, blank=True)
    mng_clean_sheets = models.IntegerField(null=True, blank=True)
    mng_goals_scored = models.IntegerField(null=True, blank=True)
    recoveries = models.IntegerField(null=True)
    tackles = models.IntegerField(null=True)
    defensive_contribution = models.IntegerField(null=True)
    clearances_blocks_interceptions = models.IntegerField(null=True)
    player = models.ForeignKey('Player', on_delete=CASCADE, null=True)
    opponent = models.ForeignKey('teams.Team', on_delete=CASCADE, null=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        """ Return a formatted representation of a players history """
        return f"{self.round} ({self.player}) v {self.opponent.short_name} " \
               f"{self.home_or_away()}: {self.team_h_score} - {self.team_a_score}"

    def home_or_away(self):
        """ Returns whether the game was Home or Away """
        return "(H)" if self.was_home else "(A)"

    def result(self):
        """ Returns a formatted string of the result of the game """
        return f"{self.team_h_score} - {self.team_a_score}" \
            if self.team_h_score is not None and self.team_a_score is not None else ""

    def game_result(self):
        """ Return Win/Lost/Draw"""

        if self.team_h_score == self.team_a_score:
            return GameResult.DRAW

        if (self.was_home and (self.team_h_score > self.team_a_score)) \
                or (not self.was_home and (self.team_a_score > self.team_h_score)):
            return GameResult.WIN

        return GameResult.LOSE


    def formatted_kickoff_time(self):
        """ Returned argument is day/month formatted """
        return day_month_year_from_datetime(self.kickoff_time)

    def full_clean(self, exclude=None, validate_unique=True):
        exclude = exclude or []
        exclude.extend(['id', 'player', 'player_id', 'opponent', 'opponent_id', 'last_updated'])
        super().full_clean(exclude=exclude, validate_unique=validate_unique)

    class Meta:
        """ Meta class for uniqueness """
        constraints = [
            models.UniqueConstraint(
                fields=['fixture', 'element'],
                name='unique_player_history'
            )
        ]
