""" This module has a Django model to store details of a Managers History.

It has details like the event, point, rank and manager (Foreign Key back to
ManagerTeam
"""

from django.db import models
from django.db.models import CASCADE

from utils.model_utils import BaseModel


class History(BaseModel):
    """ Class model to store a Managers History """

    event = models.IntegerField(null=True)
    points = models.IntegerField(null=True)
    total_points = models.IntegerField(null=True)
    rank = models.IntegerField(null=True)
    rank_sort = models.IntegerField(null=True)
    percentile_rank = models.IntegerField(null=True)
    overall_rank = models.IntegerField(null=True)
    bank = models.DecimalField(decimal_places=2, max_digits=6, null=True)
    value = models.IntegerField(null=True)
    event_transfers = models.IntegerField(null=True)
    event_transfers_cost = models.IntegerField(null=True)
    points_on_bench = models.IntegerField(null=True)
    manager = models.ForeignKey('ManagerTeam', on_delete=CASCADE, null=True)
    last_updated = models.DateTimeField(auto_now=True)

    def full_clean(self, exclude=None, validate_unique=True):
        exclude = exclude or []
        exclude.extend(['manager'])
        super().full_clean(exclude=exclude, validate_unique=validate_unique)

    class Meta:
        """ Meta class for uniqueness """
        constraints = [
            models.UniqueConstraint(
                fields=['event', 'manager'],
                name='unique_manager_history'
            )
        ]