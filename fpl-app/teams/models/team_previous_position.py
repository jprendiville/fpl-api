""" This module has a Django model to store a teams previous finishing position """

from django.db import models
from django.db.models import CASCADE

from teams.models.team import Team
from utils.model_utils import BaseModel


class TeamPreviousPosition(BaseModel):
    """ Class model to store what position a team finished last season """

    season = models.IntegerField(null=True)
    team = models.IntegerField(null=True)
    position = models.IntegerField(null=True)
    last_updated = models.DateTimeField(auto_now=True)
    this_team = models.ForeignKey(Team, on_delete=CASCADE)

    def __str__(self):
        """ Return a formatted representation of where a team finished previously """
        return f"{self.season} = {self.team.name} = {self.position}"

    def full_clean(self, exclude=None, validate_unique=True):
        exclude = exclude or []
        super().full_clean(exclude=exclude, validate_unique=validate_unique)

    class Meta:
        """ Meta class for uniqueness """

        constraints = [
            models.UniqueConstraint(
                fields=['season', 'team'],
                name='unique_team_previous_position'
            )
        ]