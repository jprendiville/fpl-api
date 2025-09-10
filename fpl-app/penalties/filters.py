""" Filters for penalty dropdowns for Gameweek """

import django_filters

from penalties.models.penalty import Penalty


class PenaltyFilter(django_filters.FilterSet):
    """ Filter used for penalties to select the gameweek """

    class Meta:
        """ Meta class to define the model and fields used for the filter """

        model = Penalty
        fields = ['gameweek']
