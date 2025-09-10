from django.db import models
from django.db.models import CASCADE

from manager.models import ClassicLeague
from utils.model_utils import BaseModel


class ClassicLeaguePhase(BaseModel):

    classic_league = models.ForeignKey(ClassicLeague, on_delete=models.CASCADE)
    manager = models.ForeignKey("ManagerTeam", on_delete=CASCADE)
    phase = models.IntegerField()
    rank = models.IntegerField(null=True)
    last_rank = models.IntegerField(null=True)
    rank_sort = models.IntegerField(null=True)
    total = models.IntegerField(null=True)
    rank_count = models.IntegerField(null=True)
    entry_percentile_rank = models.IntegerField(null=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        """ Return a formatted representation of a classic league phase """
        return f"{self.classic_league.name - self.phase}"

    def full_clean(self, exclude=None, validate_unique=True):
        exclude = exclude or []
        exclude.extend(['classic_league', 'manager'])
        super().full_clean(exclude=exclude, validate_unique=validate_unique)

    class Meta:
        """ Meta class for uniqueness """
        constraints = [
            models.UniqueConstraint(
                fields=['classic_league', 'manager', 'phase'],
                name='unique_classic_league_phase'
            )
        ]