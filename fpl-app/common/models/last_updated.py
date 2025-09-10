""" This module has a Django model to store details of when the data was last
updated.

It's used when checking if a period of time has passed to determine whether
we want to update the data or not. It is used by
properties.check_update_required to compare the datetime below and current
datetime and checked if properties.reload_full_cache_time (in minutes) has elapsed.
"""

from django.db import models


class LastUpdated(models.Model):
    """ Class model to store the last updated timestamp for FPL and prediction data """

    fpl_data = models.DateTimeField(null=True)
    live_data = models.DateTimeField(null=True)
    fixture_data = models.DateTimeField(null=True)
    prediction_data = models.DateTimeField(null=True)
