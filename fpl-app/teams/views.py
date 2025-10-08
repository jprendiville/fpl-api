import logging

from django.shortcuts import render

from common.forms import GameweekForm
from common.models.event import Event
from common.models.fixture import Fixture
from common.utils import get_current_gameweek, get_fixture_stats, \
    get_next_n_games_fdr
from fpl.dataloader.load.fpl_data import load_and_save_fixture_data
from fpl.dataloader.load.load_managers import get_live_league_standings
from fpl.properties.properties import get_properties
from teams.forms import LeagueTableForm
from teams.models import Team
from utils.sql_utils import get_league_table_by_gameweek

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

properties = get_properties()

def live_fixtures(request):
    """ Respond to a request to display fixtures """
    form = GameweekForm(request.GET or None)
    gameweek = get_current_gameweek()
    if form.is_valid():
        gameweek = form.cleaned_data.get('gameweek')

    # If it is the current gameweek, reload data
    if gameweek.is_current:
        load_and_save_fixture_data(gameweek)
        get_live_league_standings(gameweek)

    fixtures = Fixture.objects.filter(event=gameweek.id).order_by('kickoff_time', 'team_home__name')

    # For each fixture, get the player statistics and add them to a dict
    for fixture in fixtures:
        fixture.combined_stats = get_fixture_stats(gameweek, fixture)

    event = Event.objects.get(id=gameweek.id)

    context = {
        'form': form,
        'event': event,
        'fixtures': fixtures
    }

    return render(request, 'live-fixtures.html', context)
