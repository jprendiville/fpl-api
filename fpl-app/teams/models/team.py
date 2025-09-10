""" This module has a Django model to store details of a Team.

It has details like name, form and various metrics based on form, strength etc.
"""

from django.db import models
from utils.model_utils import BaseModel


class Team(BaseModel):
    """ Class model to store a Team """

    id = models.IntegerField(primary_key=True)
    strength_defence_away = models.IntegerField(null=True)
    code = models.IntegerField(null=True)
    strength = models.IntegerField(null=True)
    unavailable = models.BooleanField(default=False, null=True)
    strength_overall_away = models.IntegerField(null=True)
    draw = models.IntegerField(null=True)
    team_division = models.IntegerField(null=True, blank=True)
    played = models.IntegerField(null=True)
    pulse_id = models.IntegerField(null=True)
    strength_attack_away = models.IntegerField(null=True)
    points = models.IntegerField(null=True)
    loss = models.IntegerField(null=True)
    strength_defence_home = models.IntegerField(null=True)
    form = models.IntegerField(null=True, blank=True)
    strength_attack_home = models.IntegerField(null=True)
    strength_overall_home = models.IntegerField(null=True)
    name = models.CharField(max_length=30)
    short_name = models.CharField(max_length=3)
    position = models.IntegerField(null=True)
    win = models.IntegerField(null=True)
    next_games = models.QuerySet()
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        """ Return the team name """
        return f"{self.name}"

    def full_clean(self, exclude=None, validate_unique=True):
        exclude = exclude or []
        super().full_clean(exclude=exclude, validate_unique=validate_unique)

    class Meta:
        """ Meta class for uniqueness """
        constraints = [
            models.UniqueConstraint(
                fields=['id', 'pulse_id', 'name'],
                name='unique_team'
            )
        ]
