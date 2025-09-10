""" This module has a Django model to store Seasons """

from django.db import models

from utils.model_utils import BaseModel


class Season(BaseModel):
    """ Class model to store a Fixture """

    season = models.IntegerField(primary_key=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        """ Return a formatted representation of a fixture """
        return f"{self.season}"

    def full_clean(self, exclude=None, validate_unique=True):
        exclude = exclude or []
        super().full_clean(exclude=exclude, validate_unique=validate_unique)

    class Meta:
        """ Meta class for uniqueness """

        constraints = [
            models.UniqueConstraint(
                fields=['season'],
                name='unique_season'
            )
        ]