""" Module for Manager views """
import logging

from django import forms
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.contrib import messages

from common.utils import get_active_gameweek, get_current_gameweek, \
    get_gameweek, \
    get_last_completed_gameweek, get_next_n_games_fdr
from fpl.dataloader.load.load_managers import get_league_standings, \
    get_live_league_standings, get_or_save_manager_team
from fpl.exceptions.manager_exceptions import ManagerNotFoundError, \
    PickNotFoundError
from fpl.properties.properties import get_properties
from fpl.templatetags.custom_tags import get_total_points
from players.filters import PickerFilter
from players.models import Event, Player
from utils.message_utils import add_message
from .classes.manager import Manager
from .filters import ClassicLeagueStandingsFilter
from .forms import ManagerIdForm
from .models import ClassicLeague, Information, ManagerTeam, Pick
from .models.classic_league_standings import ClassicLeagueStandings

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

properties = get_properties()


def managers(request):
    """ Respond to a request to display a manager(s) team """
    context = {}
    managers = []

    # We want to seed the lowest and greatest values possible for fdr
    context['easiest'] = properties.fdr_easiest
    context['hardest'] = properties.fdr_hardest
    context['managers'] = managers

    current_gameweek = get_current_gameweek()
    last_completed_gameweek = get_last_completed_gameweek()
    events = Event.objects.all().filter(id__gte=current_gameweek.id).order_by('id')[:properties.number_of_gameweeks]
    context['events'] = events

    filtered_players = PickerFilter(
        request.GET,
        queryset=Player.objects.all().order_by('-ep_next')
    )
    context['filtered_players'] = filtered_players

    if request.method == 'POST':

        manageridform = ManagerIdForm(request.POST)

        try:
            if manageridform.is_valid():

                ids = [int(x) for x in manageridform.cleaned_data.split(',')]

                for manager_id in ids:
                    try:
                        managers.append(load_manager(manager_id, 0, properties.number_of_gameweeks, current_gameweek, last_completed_gameweek))
                    except PermissionDenied:
                        context = {'message': 'Updates are in progress, permission denied'}
                        return render(request, 'denied-page.html', context=context)
                context['managers'] = managers
            context['manageridform'] = manageridform
            return render(request, 'managers.html', context=context)
        except forms.ValidationError:
            context['manageridform'] = manageridform
            return render(request, 'managers.html', context=context)
        except PickNotFoundError:
            context['manageridform'] = manageridform
            messages.error(*add_message(request, 'Some player(s) for the manager were not found, suggest re-loading data', None))
            return render(request, 'managers.html', context=context)

    context['manageridform'] = ManagerIdForm()
    return render(request, 'managers.html', context=context)


def reset(request):
    """ Respond to a request to reset the manager and start afresh """
    return redirect(managers)


def leagues(request, manager_id):
    """ Respond to a request to display leagues that a given manager is in """
    context = {}
    manager_team = ManagerTeam.objects.get(id=manager_id)
    information = Information.objects.get(id=manager_id)
    classic_leagues = ClassicLeague.objects.all().filter(manager_id=manager_id).order_by('-league_type', 'league_id')
    movement = ClassicLeague.Movement

    manager = Manager(manager_team, information, classic_leagues)

    context['manager'] = manager
    context['classic_leagues'] = classic_leagues
    context['movement'] = movement

    return render(request, 'leagues.html', context=context)


def classic_league_standings(request, id, manager_id):
    """ Respond to a request to display Classic League standing for a given manager """
    context = {}

    current_gameweek = get_current_gameweek()
    event = get_last_completed_gameweek()

    # Get the managers
    try:
        page_number = int(str(request.GET.get('page')))
    except ValueError:
        page_number = 1

    try:
        gameweek = int(str(request.GET.get('gameweek')))
        event = get_gameweek(gameweek)
    except ValueError:
        pass

    get_league_standings(id, manager_id, event)

    league = ClassicLeague.objects.get(league_id=id, manager_id=manager_id)
    movement = ClassicLeague.Movement

    # Get a list of managers in the league with the filter so we can filter by gameweek
    filtered_standings = ClassicLeagueStandingsFilter(
        request.GET,
        queryset=ClassicLeagueStandings.objects.all().filter(
            league_id=id,
            gameweek=current_gameweek.id,
            gameweek__finished=True)
    )

    context['filtered_gameweek'] = filtered_standings

    league_managers = (ClassicLeagueStandings.objects.all().filter(
        league_id=id,
        gameweek=event.id).order_by('-total'))

    context['league'] = league
    context['movement'] = movement

    # We want to seed the lowest and greatest values possible for fdr
    context['easiest'] = properties.fdr_easiest
    context['hardest'] = properties.fdr_hardest

    context['gameweek'] = event.name

    managers = []
    for manager in league_managers:
        try:
            managers.append(load_manager(manager.entry, manager.league_id, 1, current_gameweek, event))
        except ManagerNotFoundError:
            # Not found, so setup a dummy manager to make the league as
            # complete as possible
            managers.append(set_dummy_manager(manager))
        except PickNotFoundError:
            messages.error(*add_message(request, 'Some player(s) for the manager were not found, suggest re-loading data', None))

    # Get this page and add the players upcoming fixtures
    paginated_filtered_standings = Paginator(managers, properties.page_size)
    page_number = request.GET.get('page')
    standing_page_obj = paginated_filtered_standings.get_page(page_number)

    context['standing_page_obj'] = standing_page_obj

    return render(request, 'league-standings.html', context=context)


def classic_league_live(request, id, manager_id):
    """ Respond to a request to display live League standing for a given manager """
    context = {}

    active_gameweek = get_active_gameweek()

    league = ClassicLeague.objects.get(league_id=id, manager_id=manager_id)
    movement = ClassicLeague.Movement
    context['league'] = league
    context['movement'] = movement
    context['gameweek'] = active_gameweek

    if not active_gameweek:
        messages.warning(*add_message(request, 'No live data, so showing latest gameweek!', None))
        return classic_league_standings(request, id, manager_id)

    # Get the managers
    try:
        page_number = int(str(request.GET.get('page')))
    except ValueError:
        page_number = 1

    get_league_standings(id, manager_id, active_gameweek)
    get_live_league_standings(active_gameweek)

    league_managers = (ClassicLeagueStandings.objects.all().filter(
        league_id=id,
        gameweek=active_gameweek.id).order_by('-total'))

    # We want to seed the lowest and greatest values possible for fdr
    context['easiest'] = properties.fdr_easiest
    context['hardest'] = properties.fdr_hardest

    managers = []
    for manager in league_managers:
        try:
            managers.append(load_manager(manager.entry, manager.league_id, 1, active_gameweek, active_gameweek))
        except ManagerNotFoundError:
            # Not found, so setup a dummy manager to make the league as
            # complete as possible
            managers.append(set_dummy_manager(manager))
        except PickNotFoundError:
            messages.error(*add_message(request, 'Some player(s) for the manager were not found, suggest re-loading data', None))

    sorted_managers = sorted(managers, key=lambda manager: get_total_points(manager.manager_team, active_gameweek, manager.this_league), reverse=True)

    # Get this page and add the players upcoming fixtures
    paginated_filtered_standings = Paginator(sorted_managers, properties.page_size)
    page_number = request.GET.get('page')
    standing_page_obj = paginated_filtered_standings.get_page(page_number)

    context['standing_page_obj'] = standing_page_obj

    return render(request, 'league-live.html', context=context)


def progression(request, id):
    """
    Generates a progression report for a specific league.

    Args:
        request (HttpRequest): The HTTP request object.
        id (int): The ID of the league.

    Returns:
        HttpResponse: The rendered HTML template for the progression report.
    """

    context = {}

    league_name = ClassicLeague.objects.filter(league_id=id).values_list('name', flat=True).first()

    # Fetch all gameweeks' data for the top 20 players
    standings = (
        ClassicLeagueStandings.objects
        .filter(league_id=id)
        .order_by('gameweek', 'player_name')
        .values('gameweek', 'player_name', 'total')
    )

    players_data = {}

    for entry in standings:
        gameweek = str(entry['gameweek'])
        player_name = entry['player_name']
        total = entry['total']

        # Initialize the year in allData if not already present
        if gameweek not in players_data:
            players_data[gameweek] = {}

        # Assign the total value to the corresponding player_name in the year
        players_data[gameweek][player_name] = total

    context['league_name'] = league_name
    context['players_data'] = players_data
    context['players_to_show'] = properties.progression_players_to_show

    return render(request, 'progression.html', context=context)


def load_manager(manager_id, league_id, number_of_gameweeks, current_gameweek, last_completed_gameweek):
    """ Load (or re-load) a managers details to the database """
    try:
        get_or_save_manager_team(league_id, manager_id, last_completed_gameweek)

    except PermissionDenied:
        # Manager not found for this gameweek, so it's the current gameweek.
        # In this scenario, load the previous gameweek with 0 points.
        raise

    manager_team = ManagerTeam.objects.get(id=manager_id)
    information = Information.objects.get(pk=manager_id)
    classic_leagues = ClassicLeague.objects.filter(manager_id=manager_id)
    this_league = ClassicLeagueStandings.objects.filter(league_id=league_id, entry=manager_id, gameweek=last_completed_gameweek).first()

    picks = Pick.objects.all().filter(manager_id=manager_id, gameweek=last_completed_gameweek.id)
    total_expected = 0
    for pick in picks:
        total_expected += pick.expected_points()
        pick.player.player_team.next_games = get_next_n_games_fdr(pick.player.player_team,
                                                                  current_gameweek,
                                                                  number_of_gameweeks)

    return Manager(manager_team, information, picks, classic_leagues, this_league, total_expected)


def set_dummy_manager(manager):
    manager_team = ManagerTeam()
    information = Information(name=manager.entry_name,
                              summary_overall_points=manager.total,
                              player_first_name=manager.player_name)
    classic_leagues = ClassicLeague()
    picks = [Pick()]
    this_league = manager
    total_expected = 0
    return Manager(manager_team, information, picks,
                            classic_leagues, this_league,
                            total_expected)


def reload_league(request, id, manager_id):
    """
    Reloads a league by deleting its existing standings and recalculating them
    based on finished and data_checked events.

    Args:
        request (HttpRequest): The HTTP request object.
        id (int): The ID of the league to reload.
        manager_id (int): The ID of the manager.

    Returns:
        HttpResponseRedirect: A redirect to the 'leagues' page with the manager
        ID as a parameter.
    """

    events = Event.objects.filter(finished=True, data_checked=True).order_by('id')

    ClassicLeagueStandings.objects.filter(league_id=id).delete()

    for event in events:
        get_league_standings(id,manager_id, event)

    return redirect('leagues', manager_id = manager_id)
