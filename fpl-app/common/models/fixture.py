""" This module has a Django model to store details of a Fixture.

It has details like kickoff time, home and away teams (Foreign key to Team),
score, fixture difficulty etc.
"""

from django.db import models
from utils import date_utils
from utils.date_utils import long_format_date_with_day
from utils.model_utils import BaseModel


class Fixture(BaseModel):
    """ Class model to store a Fixture """

    id = models.IntegerField(primary_key=True)
    code = models.IntegerField(null=True)
    event = models.IntegerField(null=True, blank=True)
    finished = models.BooleanField(null=True)
    finished_provisional = models.BooleanField(null=True)
    kickoff_time = models.DateTimeField(null=True, blank=True)
    minutes = models.IntegerField(null=True)
    provisional_start_time = models.BooleanField(null=True)
    started = models.BooleanField(null=True, blank=True)
    team_a = models.IntegerField(null=True)
    team_a_score = models.IntegerField(null=True, blank=True)
    team_h = models.IntegerField(null=True)
    team_h_score = models.IntegerField(null=True, blank=True)
    stats = models.TextField(blank=True)
    team_h_difficulty = models.IntegerField(null=True)
    team_a_difficulty = models.IntegerField(null=True)
    pulse_id = models.IntegerField(null=True)
    team_home = models.ForeignKey('teams.Team', null=True, on_delete=models.CASCADE,
                                  related_name='fix_home_team', to_field='id', blank=True)
    team_away = models.ForeignKey('teams.Team', null=True, on_delete=models.CASCADE,
                                  related_name='fix_away_team', to_field='id', blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        """ Return a formatted representation of a fixture """
        return (f"{self.formatted_kickoff()}"
                f"{self.team_home.short_name} "
                f"{self.team_away.short_name}")

    def formatted_long_format_date(self):
        """ Returned argument is day/month/year formatted """
        return long_format_date_with_day(self.kickoff_time)

    def formatted_kickoff(self):
        """ Return the formatted kick off time """
        return date_utils.formatted_datetime(self.kickoff_time)

    def formatted_kickoff_time(self):
        """ Return the formatted kick off time """
        return date_utils.formatted_time(self.kickoff_time)

    def full_clean(self, exclude=None, validate_unique=True):
        exclude = exclude or []
        super().full_clean(exclude=exclude, validate_unique=validate_unique)

    class Meta:
        """ Meta class for uniqueness """
        constraints = [
            models.UniqueConstraint(
                fields=['id', 'team_h', 'team_a'],
                name='unique_fixture'
            )
        ]
