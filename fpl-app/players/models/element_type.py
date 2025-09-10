""" This module has a Django model to store details of an element type.

An element type is a goalkeeper, defender, midfielder or forward.
"""

from django.db import models
from utils.model_utils import BaseModel


class ElementType(BaseModel):
    """ Class model to store a Element Type (ie, goalkeeper, defender,
    midfielder, forward) """

    id = models.IntegerField(primary_key=True)
    plural_name = models.CharField(max_length=32, blank=True)
    plural_name_short = models.CharField(max_length=3, blank=True)
    singular_name = models.CharField(max_length=32, blank=True)
    singular_name_short = models.CharField(max_length=3, blank=True)
    squad_select = models.IntegerField(null=True)
    squad_min_select = models.IntegerField(null=True, blank=True)
    squad_max_select = models.IntegerField(null=True, blank=True)
    squad_min_play = models.IntegerField(null=True)
    squad_max_play = models.IntegerField(null=True)
    ui_shirt_specific = models.BooleanField(default=False, null=True)
    sub_positions_locked = models.JSONField(default=list, blank=True)
    element_count = models.IntegerField(null=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        """ Return a formatted representation of an element type """
        return f"{self.plural_name}"

    def full_clean(self, exclude=None, validate_unique=True):
        exclude = exclude or []
        super().full_clean(exclude=exclude, validate_unique=validate_unique)

    class Meta:
        """ Meta class for uniqueness """

        constraints = [
            models.UniqueConstraint(
                fields=['id', 'singular_name'],
                name='unique_element_type'
            )
        ]