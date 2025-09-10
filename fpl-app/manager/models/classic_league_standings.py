""" This module has a Django model to store details of a classic league
standing.

It stores details like the league id, manager name, team name, manager id,
gameweek points, total points and gameweek (with a foreign key to Event) so we
can keep historical information.
"""

from django.db import models
from django.db.models import CASCADE

from players.models import Event
from utils.model_utils import BaseModel


class ClassicLeagueStandings(BaseModel):
    """ Class model to store a Classic League Standing """

    class Movement(models.TextChoices):
        """ TextChoice Class for rank movement """

        SAME = 'SAME', 'Same'
        UP = 'UP', 'Up'
        DOWN = 'DOWN', 'Down'

    id = models.AutoField(primary_key=True)
    league_id = models.IntegerField(null=True)
    event_total = models.IntegerField(null=True)
    has_played = models.BooleanField(default=False)
    player_name = models.CharField(max_length=128, blank=True)
    rank = models.IntegerField(null=True)
    last_rank = models.IntegerField(null=True)
    rank_sort = models.IntegerField(null=True)
    total = models.IntegerField(null=True)
    entry = models.IntegerField(null=True)
    entry_name = models.CharField(max_length=128, blank=True)
    gameweek = models.ForeignKey(Event, on_delete=CASCADE, null=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        """ Return a formatted representation of a managers classic league standing """
        return f"{self.rank} : {self.player_name} - {self.total}"

    def movement(self):
        """ Function to work out rank movement since last rank

        :return: Class Movement with SAME/UP/DOWN
        """
        if self.rank == self.last_rank:
            return self.Movement.SAME
        if self.rank < self.last_rank:
            return self.Movement.UP
        return self.Movement.DOWN

    def preprocess_data(self, data):
        if data is None:
            return ''
        return data

    def set_field_defaults(self):
        self.player_name = self.preprocess_data(self.player_name)
        self.entry_name = self.preprocess_data(self.entry_name)

    def full_clean(self, exclude=None, validate_unique=True):
        exclude = exclude or []
        exclude.extend(['id', 'gameweek'])
        super().full_clean(exclude=exclude, validate_unique=validate_unique)

    class Meta:
        """ Meta class for uniqueness """
        constraints = [
            models.UniqueConstraint(
                fields=['id', 'gameweek'],
                name='unique_classic_league_standing'
            )
        ]
        ordering = ['rank']