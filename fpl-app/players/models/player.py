""" This module is a Django Model to store details about players.

It has details like the name, team (ForeignKey to Player), type ((ForeignKey to
ElementType), cost, points and a whole lot more. One of the core models in the
application.
"""
import decimal

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import CASCADE

from manager.classes.league_standings import LeagueStandings
from players.models.element_type import ElementType
from teams.models.team import Team
from utils.model_utils import BaseModel


class Player(BaseModel):
    """ Class to store Player details """

    id = models.IntegerField(primary_key=True)
    own_goals = models.IntegerField(null=True)
    bonus = models.IntegerField(null=True)
    total_points = models.IntegerField(null=True)
    corners_and_indirect_freekicks_order = models.IntegerField(null=True, blank=True)
    influence = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    creativity_rank = models.IntegerField(null=True)
    squad_number = models.IntegerField(null=True, blank=True)
    saves = models.IntegerField(null=True)
    transfers_in = models.IntegerField(null=True)
    value_form = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    penalties_text = models.CharField(max_length=128, blank=True)
    now_cost = models.IntegerField(null=True)
    now_cost_rank = models.IntegerField(null=True)
    now_cost_rank_type = models.IntegerField(null=True)
    creativity = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    influence_rank = models.IntegerField(null=True)
    goals_scored = models.IntegerField(null=True)
    minutes = models.IntegerField(null=True)
    yellow_cards = models.IntegerField(null=True)
    selected_by_percent = models.DecimalField(max_digits=6,
                                              decimal_places=2,
                                              null=True)
    selected_rank = models.IntegerField(null=True)
    selected_rank_type = models.IntegerField(null=True)
    threat_rank_type = models.IntegerField(null=True)
    corners_and_indirect_freekicks_text = models.CharField(max_length=128,
                                                           blank=True)
    ict_index_rank_type = models.IntegerField(null=True)
    in_dreamteam = models.BooleanField(default=False, null=True)
    cost_change_event_fall = models.IntegerField(null=True)
    ict_index_rank = models.IntegerField(null=True)
    second_name = models.CharField(max_length=64, blank=True)
    cost_change_event = models.IntegerField(null=True)
    points_per_game = models.DecimalField(max_digits=6,
                                          decimal_places=2,
                                          null=True)
    points_per_game_rank = models.IntegerField(null=True)
    points_per_game_rank_type = models.IntegerField(null=True)
    web_name = models.CharField(max_length=64, blank=True)
    status = models.CharField(max_length=10, blank=True)
    chance_of_playing_this_round = models.IntegerField(default=100, blank=True)
    code = models.IntegerField(null=True)
    clean_sheets = models.IntegerField(null=True)
    goals_conceded = models.IntegerField(null=True)
    cost_change_start = models.IntegerField(null=True)
    red_cards = models.IntegerField(null=True)
    element_type = models.IntegerField(null=True)
    direct_freekicks_text = models.CharField(max_length=128, blank=True)
    dreamteam_count = models.IntegerField(null=True)
    threat_rank = models.IntegerField(null=True)
    assists = models.IntegerField(null=True)
    penalties_order = models.IntegerField(null=True, blank=True)
    ep_this = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    chance_of_playing_next_round = models.IntegerField(default=100, blank=True)
    first_name = models.CharField(max_length=64, blank=True)
    news_added = models.DateTimeField(null=True, blank=True)
    direct_freekicks_order = models.IntegerField(null=True, blank=True)
    news = models.CharField(max_length=128, blank=True)
    bps = models.IntegerField(null=True)
    ep_next = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    transfers_out_event = models.IntegerField(null=True)
    penalties_missed = models.IntegerField(null=True)
    photo = models.CharField(max_length=64, blank=True)
    transfers_in_event = models.IntegerField(null=True)
    team = models.IntegerField(null=True)
    cost_change_start_fall = models.IntegerField(null=True)
    event_points = models.IntegerField(null=True)
    influence_rank_type = models.IntegerField(null=True)
    creativity_rank_type = models.IntegerField(null=True)
    special = models.BooleanField(default=False, null=True)
    team_code = models.IntegerField(null=True)
    transfers_out = models.IntegerField(null=True)
    form = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    form_rank = models.IntegerField(null=True)
    form_rank_type = models.IntegerField(null=True)
    threat = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    value_season = models.DecimalField(max_digits=6,
                                       decimal_places=2,
                                       null=True)
    ict_index = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    starts = models.IntegerField(null=True)
    starts_per_90 = models.DecimalField(max_digits=6,
                                        decimal_places=2,
                                        null=True)
    saves_per_90 = models.DecimalField(max_digits=6,
                                       decimal_places=2,
                                       null=True)
    goals_conceded_per_90 = models.DecimalField(max_digits=6,
                                                decimal_places=2,
                                                null=True)
    clean_sheets_per_90 = models.DecimalField(max_digits=6,
                                              decimal_places=2,
                                              null=True)
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
    expected_goals_per_90 = models.DecimalField(max_digits=6,
                                                decimal_places=2,
                                                null=True)
    expected_assists_per_90 = models.DecimalField(max_digits=6,
                                                  decimal_places=2,
                                                  null=True)
    expected_goal_involvements_per_90 = models.DecimalField(max_digits=6,
                                                            decimal_places=2,
                                                            null=True)
    expected_goals_conceded_per_90 = models.DecimalField(max_digits=6,
                                                         decimal_places=2,
                                                         null=True)
    penalties_saved = models.IntegerField(null=True)
    can_transact = models.BooleanField(default=False)
    can_select = models.BooleanField(default=False)
    removed = models.BooleanField(default=False)
    player_team = models.ForeignKey(Team, on_delete=CASCADE, null=True, blank=True)
    player_type = models.ForeignKey(ElementType, on_delete=CASCADE, null=True, blank=True)
    vapm = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    region = models.IntegerField(null=True, blank=True)
    opta_code = models.CharField(max_length=64, blank=True)
    mng_win = models.IntegerField(null=True, blank=True)
    mng_draw = models.IntegerField(null=True, blank=True)
    mng_loss = models.IntegerField(null=True, blank=True)
    mng_underdog_win = models.IntegerField(null=True, blank=True)
    mng_underdog_draw = models.IntegerField(null=True, blank=True)
    mng_clean_sheets = models.IntegerField(null=True, blank=True)
    mng_goals_scored = models.IntegerField(null=True, blank=True)
    has_temporary_code = models.BooleanField(default=False)
    team_join_date = models.DateField(null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    clearances_blocks_interceptions = models.IntegerField(null=True)
    recoveries = models.IntegerField(null=True)
    tackles = models.IntegerField(null=True)
    defensive_contribution = models.IntegerField(null=True)
    defensive_contribution_per_90 = models.IntegerField(null=True)

    last_updated = models.DateTimeField(auto_now=True)
    history_last_updated = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        """ Return a formatted representation of a player """
        return f"{self.web_name} ({self.player_team.short_name})"

    def shortened_name(self):
        """ Return a shortened name if it is > 10 """
        if len(self.web_name) > 10:
            return f"{self.web_name[:10]}..."
        return f"{self.web_name[:20]}"

    def points_per_minute(self):
        """ Return points per minute """
        if self.total_points == 0:
            return 0
        return round(self.total_points / 90, 2)

    def points_per_90minute(self):
        """ Return points per 90 minutes """
        if self.minutes == 0:
            return 0
        return round(self.total_points / (self.minutes / 90), 2)

    def points_per_cost(self):
        """ Return points per cost """
        if self.now_cost == 0:
            return 0
        return f"{round(self.total_points / (self.now_cost / 10), 2):.2f}"

    def points_per_match_per_m(self):
        """ Return points per game per million """
        if self.now_cost == 0:
            return 0
        return round(self.points_per_game / self.now_cost / 10, 2)

    def points_value_added_per_m(self):
        """ Return value added per million.

        This takes 2 points off a players point_per_game, to take away the 2
        points for playing 60 minutes. It's a way of disregarding subs.
        """

        # Ensure that both point_per_game and now_cost are decimals (they are
        # possibly strings or floats from incoming data
        try:
            ppg = decimal.Decimal(self.points_per_game)
        except ValueError:
            return 0

        try:
            nc = decimal.Decimal(self.now_cost / 10)
        except ValueError:
            return 0

        if self.now_cost == 0:
            return 0

        return round((ppg - 2) / nc, 2)

    def formatted_cost(self):
        """ Return cost formatted """
        return f"£{self.now_cost / 10:.2f}"

    def get_player_history(self):
        """ Return the players history """
        return sorted(
            list(self.playerhistory_set),
            key=lambda x: x.fixture.id,
            reverse=True
        )

    def get_player_prediction_history(self):
        """ Return the players prediction history """
        return sorted(
            list(self.playerprediction_set.filter(finished=True)),
            key=lambda x: x.gameweek.id,
            reverse=True
        )

    def get_player_live_points(self, gameweek):
        try:
            if LeagueStandings.bonus_added(gameweek):
                return self.classicleaguelivestandings.total_points
            return self.classicleaguelivestandings.total_points + self.classicleaguelivestandings.bonus
        except ObjectDoesNotExist:
            # Return a default value if ClassicLeagueLiveStandings does not exist
            return 0

    def get_player_live_bonus(self):
        try:
            return self.classicleaguelivestandings.bonus
        except ObjectDoesNotExist:
            # Return a default value if ClassicLeagueLiveStandings does not exist
            return 0

    def clean_sheet_benefit(self):
        """ Asks the question if a player gets the benefit of a clean sheet """
        return True if self.element_type <= 3 else False

    def get_formatted_news(self):
        """ Returns the news of a player (maybe be transferred to another
         league etc) """
        if self.status == 'a':
            return 'Available'
        return self.news

    def formatted_old_cost(self):
        """ Return old cost formatted """
        return f"£{((self.now_cost / 10) - round(self.cost_change_event / 10, 2)):.2f}"

    def formatted_price_change(self):
        """ Return price change formatted """
        return f"£{self.cost_change_event / 10}"

    def full_clean(self, exclude=None, validate_unique=True):
        exclude = exclude or []
        exclude.extend(['player_team', 'player_type'])
        super().full_clean(exclude=exclude, validate_unique=validate_unique)

    class Meta:
        """ Meta class for ordering """
        constraints = [
            models.UniqueConstraint(
                fields=['id'],
                name='unique_player'
            )
        ]
        ordering = ["-player_type", "web_name"]


    def save(self, *args, **kwargs):
        # List of fields to set default values if they are None
        fields_to_set_default = ['chance_of_playing_this_round', 'chance_of_playing_next_round']

        for field_name in fields_to_set_default:
            # Get the field value
            field_value = getattr(self, field_name)

            # Set default value if the field is None
            if field_value is None:
                setattr(self, field_name, self._meta.get_field(field_name).default)

        # Call the original save method
        super().save(*args, **kwargs)
