""" This module has a Django model to store details of a Managers Information.

It has details like name, favourite team, points etc.
"""

from django.db import models

from utils.model_utils import BaseModel


class Information(BaseModel):
    """ Class model to store a Managers Information """

    joined_time = models.DateTimeField(null=True)
    started_event = models.IntegerField(null=True)
    favourite_team = models.IntegerField(null=True)
    player_first_name = models.CharField(max_length=32, blank=True)
    player_last_name = models.CharField(max_length=32, blank=True)
    player_region_id = models.IntegerField(null=True)
    player_region_name = models.CharField(max_length=32, blank=True)
    player_region_iso_code_short = models.CharField(max_length=32, blank=True)
    player_region_iso_code_long = models.CharField(max_length=32, blank=True)
    summary_overall_points = models.IntegerField(null=True)
    summary_overall_rank = models.IntegerField(null=True)
    summary_event_points = models.IntegerField(null=True)
    summary_event_rank = models.IntegerField(null=True)
    current_event = models.IntegerField(null=True)
    name = models.CharField(max_length=32, blank=True)
    name_change_blocked = models.BooleanField(null=True, default=False)
    kit = models.CharField(max_length=255, blank=True)
    last_deadline_bank = models.IntegerField(null=True)
    last_deadline_value = models.IntegerField(null=True)
    last_deadline_total_transfers = models.IntegerField(null=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        """ Return a formatted representation of a managers information """
        return f"{self.player_first_name} {self.player_last_name} - {self.name}"

    def formatted_name(self):
        """ Return the players name formatted """
        return f"{self.player_first_name} {self.player_last_name}"

    def preprocess_data(self, data):
        if data is None:
            return ''
        return data

    def set_field_defaults(self):
        self.player_first_name = self.preprocess_data(self.player_first_name)
        self.player_last_name = self.preprocess_data(self.player_last_name)
        self.player_region_name = self.preprocess_data(self.player_region_name)
        self.player_region_iso_code_short = self.preprocess_data(self.player_region_iso_code_short)
        self.player_region_iso_code_long = self.preprocess_data(self.player_region_iso_code_long)
        self.name = self.preprocess_data(self.name)
        self.kit = self.preprocess_data(self.kit)

    def full_clean(self, exclude=None, validate_unique=True):
        exclude = exclude or []
        super().full_clean(exclude=exclude, validate_unique=validate_unique)

    class Meta:
        """ Meta class for uniqueness """
        constraints = [
            models.UniqueConstraint(
                fields=['id'],
                name='unique_manager_information'
            )
        ]