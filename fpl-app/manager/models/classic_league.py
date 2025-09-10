""" This module has a Django model to store details of a classic league.

It stores details like the league id, manager (with a foreign key to
ManagerTeam), points, rank etc.
"""

from django.db import models
from django.db.models import CASCADE

from utils.model_utils import BaseModel


class ClassicLeague(BaseModel):
    """ Class model to store a Classic League """

    class Movement(models.TextChoices):
        """ TextChoice Class for rank movement """

        SAME = 'SAME', 'Same'
        UP = 'UP', 'Up'
        DOWN = 'DOWN', 'Down'

    league_id = models.IntegerField(null=True, blank=True)
    manager = models.ForeignKey("ManagerTeam", on_delete=CASCADE, null=True)
    name = models.CharField(max_length=128, blank=True)
    short_name = models.CharField(max_length=32, blank=True, null=True)
    created = models.DateTimeField(null=True)
    closed = models.BooleanField(default=False)
    rank = models.IntegerField(null=True, blank=True)
    max_entries = models.IntegerField(null=True, blank=True)
    league_type = models.CharField(max_length=1, blank=True)
    scoring = models.CharField(max_length=1, blank=True)
    admin_entry = models.IntegerField(null=True, blank=True)
    start_event = models.IntegerField(null=True)
    entry_can_leave = models.BooleanField(default=True)
    entry_can_admin = models.BooleanField(default=False)
    entry_can_invite = models.BooleanField(default=False)
    has_cup = models.BooleanField(default=False)
    cup_league = models.IntegerField(null=True, blank=True)
    cup_qualified = models.IntegerField(null=True, blank=True)
    rank_count = models.IntegerField(null=True, blank=True)
    entry_rank = models.IntegerField(null=True)
    entry_last_rank = models.IntegerField(null=True)
    entry_percentile_rank = models.IntegerField(null=True, blank=True)
    active_phases = models.JSONField(default=list)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        """ Return a formatted representation of a classic league """
        return f"{self.name}"

    def movement(self):
        """ Function to return the rank movement since last rank """
        if self.entry_rank == self.entry_last_rank:
            return self.Movement.SAME
        if self.entry_rank < self.entry_last_rank:
            return self.Movement.UP
        return self.Movement.DOWN

    def full_clean(self, exclude=None, validate_unique=True):
        exclude = exclude or []
        exclude.extend(['manager', 'id'])
        super().full_clean(exclude=exclude, validate_unique=validate_unique)

    class Meta:
        """ Meta class for uniqueness """

        constraints = [
            models.UniqueConstraint(
                fields=['league_id', 'manager'],
                name='unique_classic_league'
            )
        ]

    def preprocess_data(self, data):
        if data is None:
            return ''
        return data

    def set_field_defaults(self):
        self.name = self.preprocess_data(self.name)
        self.short_name = self.preprocess_data(self.short_name)
        self.league_type = self.preprocess_data(self.league_type)
        self.scoring = self.preprocess_data(self.scoring)
