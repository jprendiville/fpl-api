""" This module is a Django Model to store details about tweets.

"""

from django.db import models

from utils.model_utils import BaseModel


class Tweet(BaseModel):
    """ Class to store Tweet details """

    id = models.IntegerField(primary_key=True)
    gameweek = models.IntegerField(null=True)
    predictions_media_id = models.IntegerField(null=True)
    actuals_media_id = models.IntegerField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


    def full_clean(self, exclude=None, validate_unique=True):
        exclude = exclude or []
        super().full_clean(exclude=exclude, validate_unique=validate_unique)

    class Meta:
        """ Meta class for uniqueness """

        constraints = [
            models.UniqueConstraint(
                fields=['id'],
                name='unique_tweet'
            )
        ]