""" Module for Player views """
import logging

from bootstrap_modal_forms.generic import BSModalReadView
from django.core.paginator import Paginator
from django.db.models import F, Func, Max
from django.shortcuts import render

from common.utils import get_current_gameweek, get_last_gameweek, \
    get_next_gameweek, \
    get_next_n_games_fdr
from fpl.properties.properties import get_properties
from players.filters import PickerFilter, PlayerFilter, \
    PredictionEvaluatorFilter, PredictionsFilter
from players.models import Event, Player, PlayerPrediction

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

properties = get_properties()


class PlayerHistoryView(BSModalReadView):
    """ Class for Player History View Modal """

    model = Player
    pk_url_kwarg = 'pk'
    template_name = 'player-history.html'

    def get_queryset(self):
        """ Return the player """
        return super().get_queryset().filter(id=self.kwargs['pk'])


class PlayerPredictionHistoryView(BSModalReadView):
    """ Class for Player Prediction History View Modal """

    model = PlayerPrediction
    pk_url_kwarg = 'pk'
    template_name = 'player-prediction-history.html'

    def get_queryset(self):
        """
        Return the player prediction evaluator based on the 'element' field.
        """
        return super().get_queryset().filter(id=self.kwargs['pk'])


def transfers(request):
    """ Respond to a request to display transfers In/Out """
    context = {}

    # Get the next game week
    next_gameweek = get_current_gameweek()
    events = Event.objects.all().filter(id__gte=next_gameweek.id).order_by('id')[
             :properties.number_of_gameweeks]
    context['events'] = events

    filtered_transfers_in = PlayerFilter(
        request.GET,
        queryset=Player.objects.all().order_by('-transfers_in_event')
    )
    filtered_transfers_out = PlayerFilter(
        request.GET,
        queryset=Player.objects.all().order_by('-transfers_out_event')
    )
    context['filtered_transfers_in'] = filtered_transfers_in
    context['filtered_transfers_out'] = filtered_transfers_out

    # Get this page
    page_number = request.GET.get('page')
    paginated_filtered_players_in = Paginator(filtered_transfers_in.qs, properties.page_size)
    paginated_filtered_players_out = Paginator(filtered_transfers_out.qs, properties.page_size)

    transfers_in_page_obj = paginated_filtered_players_in.get_page(page_number)
    transfers_out_page_obj = paginated_filtered_players_out.get_page(page_number)

    context['transfers_in_page_obj'] = transfers_in_page_obj
    context['transfers_out_page_obj'] = transfers_out_page_obj

    return render(request, 'transfers.html', context=context)


def price_changes(request):
    """ Respond to a request to display price changes """
    context = {}

    # Get the next game week
    next_gameweek = get_current_gameweek()
    events = Event.objects.all().filter(id__gte=next_gameweek.id).order_by('id')[
             :properties.number_of_gameweeks]
    context['events'] = events

    filtered_price_increases = PlayerFilter(
        request.GET,
        queryset=Player.objects.all().order_by('-cost_change_event', '-selected_by_percent')
    )
    filtered_price_decreases = PlayerFilter(
        request.GET,
        queryset=Player.objects.all().order_by('-cost_change_event_fall', '-selected_by_percent')
    )
    context['filtered_price_increases'] = filtered_price_increases
    context['filtered_price_decreases'] = filtered_price_decreases

    # Because both page obj can be different sizes, use the largest to do pagination
    largest_page_obj = filtered_price_increases \
        if len(filtered_price_increases.qs) > len(filtered_price_decreases.qs) \
        else filtered_price_decreases
    context['largest_page_obj'] = largest_page_obj

    # Get this page
    page_number = request.GET.get('page')
    paginated_filtered_price_increases = Paginator(filtered_price_increases.qs,
                                                   properties.page_size)
    paginated_filtered_price_decreases = Paginator(filtered_price_decreases.qs,
                                                   properties.page_size)

    price_increases_page_obj = paginated_filtered_price_increases.get_page(page_number)
    price_decreases_page_obj = paginated_filtered_price_decreases.get_page(page_number)

    context['price_increases_page_obj'] = price_increases_page_obj
    context['price_decreases_page_obj'] = price_decreases_page_obj

    return render(request, 'price-changes.html', context=context)

def picker(request):
    """ Respond to a request to display player picker """
    context = {}

    # Get the next game week
    next_gameweek = get_next_gameweek()
    events = Event.objects.all().filter(id__gte=next_gameweek.id).order_by('id')[
             :properties.number_of_gameweeks]
    context['events'] = events

    filtered_players = PickerFilter(
        request.GET,
        queryset=Player.objects.all().order_by('-ep_next')
    )
    context['filtered_players'] = filtered_players

    # We want to seed the lowest and greatest values possible for fdr
    context['easiest'] = properties.fdr_easiest
    context['hardest'] = properties.fdr_hardest

    # Get this page and add the players upcomign fixtures
    paginated_filtered_players = Paginator(filtered_players.qs, properties.page_size)
    page_number = request.GET.get('page')
    player_page_obj = paginated_filtered_players.get_page(page_number)
    for player in player_page_obj.object_list:
        player.player_team.next_games = \
            get_next_n_games_fdr(player.player_team, next_gameweek, properties.number_of_gameweeks)
    context['player_page_obj'] = player_page_obj

    return render(request, 'picker.html', context=context)


def predictions(request):
    """ Respond to a request to display player data by Total Points """
    context = {}

    # Get the next game week
    gameweek = get_last_gameweek()
    events = Event.objects.all().filter(id__gte=gameweek.id).order_by('id')[
             :properties.number_of_gameweeks]
    context['events'] = events

    # Load the predictions
    filtered_players = PredictionsFilter(
        request.GET,
        queryset=PlayerPrediction.objects.filter
            (gameweek_id=PlayerPrediction.objects.aggregate(Max('gameweek_id')).
             get('gameweek_id__max')).order_by('-prediction')
    )
    context['filtered_players'] = filtered_players

    # We want to seed the lowest and greatest values possible for fdr
    context['easiest'] = properties.fdr_easiest
    context['hardest'] = properties.fdr_hardest

    # Get this page and add the players upcomign fixtures
    paginated_filtered_players = Paginator(filtered_players.qs, properties.page_size)
    page_number = request.GET.get('page')
    player_page_obj = paginated_filtered_players.get_page(page_number)
    for player in player_page_obj.object_list:
        player.player.player_team.next_games = \
            get_next_n_games_fdr(player.player.player_team, gameweek,
                                 properties.number_of_gameweeks)
    context['player_page_obj'] = player_page_obj

    return render(request, 'predictions.html', context=context)

def prediction_evaluator(request):
    """ Respond to a request to display player data by Total Points """
    context = {}

    # Calculate accuracy. This will be where a players actual points >
    # predicted points
    total_count = PredictionEvaluatorFilter(
        request.GET,
        queryset=PlayerPrediction.objects.filter(finished=True)
    ).qs.count()
    accuracy = PredictionEvaluatorFilter(
        request.GET,
        queryset=PlayerPrediction.objects.filter(total_points__gte=
                            Func(F('prediction'), function='FLOOR'),
                                                 finished=True)
    ).qs.count()
    context['accuracy'] = accuracy
    context['total_count'] = total_count
    try:
        context['percent'] = round((accuracy / total_count) * 100,2)
    except ZeroDivisionError:
        context['percent'] = 0

    # Load the predictions
    filtered_players = PredictionEvaluatorFilter(
        request.GET,
        queryset=PlayerPrediction.objects.filter(finished=True).order_by('-prediction')
    )
    context['filtered_players'] = filtered_players

    # We want to seed the lowest and greatest values possible for fdr
    context['easiest'] = properties.fdr_easiest
    context['hardest'] = properties.fdr_hardest

    # Get this page and add the players upcomign fixtures
    paginated_filtered_players = Paginator(filtered_players.qs, properties.page_size)
    page_number = request.GET.get('page')
    player_page_obj = paginated_filtered_players.get_page(page_number)
    context['player_page_obj'] = player_page_obj

    return render(request, 'prediction-evaluator.html', context=context)




