""" This module has a Django model to store details of a Fixture.

It has details like kickoff time, home and away teams (Foreign key to Team),
score, fixture difficulty etc.
"""

from django.db import models

from fpl.enums.common_enums import FixtureStatIdentifier, HomeAwayIdentifier
from utils.model_utils import BaseModel


class FixtureStats(BaseModel):
    """ Class model to store a Fixture statistics"""

    fixture = models.ForeignKey('Fixture', on_delete=models.CASCADE, related_name='fixture_stats')
    identifier = models.CharField(max_length=50, choices=FixtureStatIdentifier.choices())
    player = models.ForeignKey('players.Player', on_delete=models.CASCADE)
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE)
    value = models.IntegerField()
    home_or_away = models.CharField(max_length=4, choices=HomeAwayIdentifier.choices())
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.identifier} - {self.player} ({self.value}) - {self.home_or_away}"

    def full_clean(self, exclude=None, validate_unique=True):
        exclude = exclude or []
        super().full_clean(exclude=exclude, validate_unique=validate_unique)

    class Meta:
        """ Meta class for uniqueness """

        constraints = [
            models.UniqueConstraint(
                fields=['fixture', 'identifier', 'player', 'team'],
                name='unique_fixture_stat'
            )
        ]
