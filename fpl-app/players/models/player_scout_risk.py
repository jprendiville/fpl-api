from django.db import models

from common.models.event import Event
from players.models import Player


class PlayerScoutRisk(models.Model):
    player = models.ForeignKey(Player, related_name="scout_risks", on_delete=models.CASCADE)
    gameweek = models.ForeignKey(Event, related_name="scout_risks", on_delete=models.CASCADE)
    property = models.CharField(max_length=100)
    notes = models.TextField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.player.web_name} - {self.property} (GW{self.gameweek})"
