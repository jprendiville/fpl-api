""" Filters for player dropdowns for the Player and Picker pages """
from django_filters import CharFilter, FilterSet, NumberFilter, \
    ModelChoiceFilter

from common.models.event import Event
from players.models import PlayerPrediction
from players.models.player import Player


class PlayerFilter(FilterSet):
    """ Filter used on the player pages to select by player type or team """
    max_cost = NumberFilter(field_name='now_cost', lookup_expr='lte',
                            label="Maximum cost")

    class Meta:
        """ Meta class to define the model and fields used for the Filter """
        model = Player
        fields = ['player_type', 'player_team', 'max_cost']
        order_by = ['player_team']


class PredictionsFilter(FilterSet):
    """ Filter used on the player pages to select by player type or team """

    class Meta:
        """ Meta class to define the model and fields used for the Filter """
        model = PlayerPrediction
        fields = ['player__player_type','player__player_team']
        order_by = ['player__player_team']


class PredictionEvaluatorFilter(FilterSet):
    """ Filter used on the prediction page to select by prediction or total points """
    gameweek = ModelChoiceFilter(queryset=Event.objects.filter(finished=True)
                                 .order_by('-id'), label='Select Gameweek')
    prediction = NumberFilter(field_name='prediction', lookup_expr='gte')
    total_points = NumberFilter(field_name='total_points', lookup_expr='gte')

    class Meta:
        """ Meta class to define the model and fields used for the Filter """
        model = PlayerPrediction
        fields = ['season', 'gameweek', 'prediction', 'player__player_type',
                  'player__player_team']


class PickerFilter(FilterSet):
    """ Filter used on the player pages to select by player type or team """
    web_name = CharFilter(lookup_expr='icontains')

    class Meta:
        """ Meta class to define the model and fields used for the Filter """
        model = Player
        fields = ['player_type', 'player_team', 'web_name']
        order_by = ['player_team']
