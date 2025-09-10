""" This module has a Django model to store details of an element type.

An element type is a goalkeeper, defender, midfielder or forward.
"""
from django.db import models
from utils.date_utils import day_month_from_datetime, \
    day_month_time_from_datetime, long_format_date
from utils.model_utils import BaseModel


class Event(BaseModel):
    """ Class model to store an Event (ie. a gameweek and associated details) """

    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=20, blank=True)
    deadline_time = models.DateTimeField(null=True)
    release_time = models.DateTimeField(null=True, blank=True)
    average_entry_score = models.IntegerField(null=True)
    finished = models.BooleanField(default=False)
    data_checked = models.BooleanField(default=False)
    highest_scoring_entry = models.IntegerField(null=True, blank=True)
    deadline_time_epoch = models.IntegerField(null=True)
    deadline_time_game_offset = models.IntegerField(null=True)
    highest_score = models.IntegerField(null=True, blank=True)
    is_previous = models.BooleanField(default=False)
    is_current = models.BooleanField(default=False)
    is_next = models.BooleanField(default=False)
    cup_leagues_created = models.BooleanField(default=False)
    h2h_ko_matches_created = models.BooleanField(default=False)
    ranked_count = models.IntegerField(null=True)
    chip_plays = models.JSONField(default=list, blank=True)
    most_selected = models.IntegerField(null=True, blank=True)
    most_transferred_in = models.IntegerField(null=True, blank=True)
    top_element = models.IntegerField(null=True, blank=True)
    top_element_info = models.JSONField(null=True, blank=True)
    transfers_made = models.IntegerField(null=True)
    most_captained = models.IntegerField(null=True, blank=True)
    most_vice_captained = models.IntegerField(null=True, blank=True)
    can_enter = models.BooleanField(default=False)
    can_manage = models.BooleanField(default=False)
    released = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        """ Return a formatted representation of an event """
        return f"{self.id}"

    def formatted_deadline(self):
        """ Returned argument is day/month formatted """
        return day_month_time_from_datetime(self.deadline_time)

    def formatted_long_format_date(self):
        """ Returned argument is day/month/year formatted """
        return long_format_date(self.deadline_time)

    def formatted_deadline_daymonth(self):
        """ Returned argument is day/month formatted """
        return day_month_from_datetime(self.deadline_time)

    def full_event(self):
        """ Returned argument is gameweek and deadline time """
        return f"{self.id} - {self.deadline_time}"

    def full_clean(self, exclude=None, validate_unique=True):
        exclude = exclude or []
        exclude.extend(['last_updated'])
        super().full_clean(exclude=exclude, validate_unique=validate_unique)

    class Meta:
        """ Meta class for uniqueness """
        constraints = [
            models.UniqueConstraint(
                fields=['id'],
                name='unique_event'
            )
        ]