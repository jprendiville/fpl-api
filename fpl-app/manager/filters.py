""" Filters for Classic League Standings dropdowns for Gameweek """

import django_filters
from django_filters import ModelChoiceFilter

from common.models.event import Event
from manager.models import ClassicLeagueStandings


class ClassicLeagueStandingsFilter(django_filters.FilterSet):
    """ Filter used on the Classic League Standings pages """
    gameweek = ModelChoiceFilter(queryset=Event.objects.filter(finished=True)
                                 .order_by('-id'), label='Select Gameweek')

    class Meta:
        """ Meta class to define the model and fields used for the filter """

        model = ClassicLeagueStandings
        fields = ['gameweek']
