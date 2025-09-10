import pandas
from django.db.models import Q

from fpl.enums.common_enums import FixtureStatIdentifier
from players.classes.opponent import Opponent
from players.models import Event, Fixture


def get_last_completed_gameweek():
    """ Returned argument is last completed gameweek """
    return Event.objects.filter(finished=True).order_by('-id').first()

def get_last_gameweek():
    """ Returned argument is last gameweek """
    return Event.objects.filter(Q(is_current=True) | Q(is_next=True)).first()

def get_current_gameweek():
    """ Returned argument is current gameweek, or next if beginning of the season """
    current_gameweek_query = Event.objects.filter(
        (Q(is_current=True) & Q(finished=False)) | Q(is_next=True)
    )

    current_gameweek = current_gameweek_query.first()
    return current_gameweek if current_gameweek else get_last_completed_gameweek()

def get_active_gameweek():
    """ Return argument is the current active gameweek """
    return Event.objects.filter(Q(is_current=True) & Q(finished=False)).first()

def get_next_gameweek():
    """ Returned argument is current gameweek, or next if beginning of the season """
    return Event.objects.filter(is_next=True).first()

def get_gameweek(id):
    """ Returned argument is specified gameweek """
    return Event.objects.get(id=id)


def get_next_n_games_fdr(team, next_gameweek, number_of_gameweeks):
    """
    Function to get the next number_of_games for a team

    :param team: the team we are looking up
    :param next_gameweek: the next gameweek
    :param number_of_gameweeks: The number of gameweeks to lookup
    :return: A Dataframe of this teams next number_of_games games
    """

    # Get the next n gameweek events
    gameweeks = Event.objects.filter(id__gte=next_gameweek.id).order_by('id')[:number_of_gameweeks]

    # This will be a DataFrame of the teams games. It's prepopulated with gameweek ids
    games = pandas.DataFrame(gameweeks.values('id'), columns=['event', 'opponents']).astype({'opponents': 'object'})

    # For each gameweek, get the teams opponenets (could be multiple)
    for gameweek in gameweeks.iterator():

        # Get a filtered list of this teams next n gameweeks
        gameweek_games = Fixture.objects.filter(event=gameweek.id)
        this_teams_gameweek_games = \
            gameweek_games.filter(Q(team_home_id=team.id) | Q(team_away_id=team.id))

        for team_game in this_teams_gameweek_games:
            # Is there anything in this gameweek?
            # If not the prepopulated dataframe will have an empty entry, which if fine.
            if team_game:
                # Home or Away?
                opponent = Opponent(team_game.event)
                if team_game.team_away_id == team.id:
                    oppo_str = team_game.team_home.short_name + ' (A)'
                    oppo_fdr = team_game.team_a_difficulty
                else:
                    oppo_str = team_game.team_away.short_name + ' (H)'
                    oppo_fdr = team_game.team_h_difficulty

                # Do we already have an entry? If so, update it. The calculation on the index
                # below is to equate the gameweek id to an index of the DataFrame. So if the
                # starting gameweek is 22 and this gameweek is 22 we want the index to be 0.
                # If this gameweek is 24 we want the index to be 2
                index = team_game.event - next_gameweek.id
                if team_game.event in games.event.values:
                    games.iloc[index]['opponents'].add_team(oppo_str)
                    games.iloc[index]['opponents'].color = 999
                    games.iloc[index]['opponents'].fdr += oppo_fdr
                else:
                    opponent.add_team(oppo_str)
                    opponent.color = oppo_fdr
                    opponent.fdr = oppo_fdr
                    games.loc[index] = [opponent.event, opponent]

    return games


def get_fixture_stats(gameweek, fixture):
    """

    :param gameweek: the gameweek being processed
    :param fixture: the particular fixture in the gamewek
    :return: A combined list of statistics for players in a fixture
    """

    def add_stat_to_group(group, stat_type, player_name, stat_value):
        ''' Helper function to add a players statistics to either home
            or away team for a fixture'''
        if stat_value > 0:
            group[stat_type.value].append({
                'name': player_name,
                'value': stat_value
            })

    home_stats_grouped = {stat.value: [] for stat in FixtureStatIdentifier}
    away_stats_grouped = {stat.value: [] for stat in FixtureStatIdentifier}

    # Depending on whether this is the current gameweek or finished gameweek,
    # the data is stored differently.
    if gameweek.is_current:
        players_home = fixture.team_home.player_set.all()
        players_away = fixture.team_away.player_set.all()
    else:
        players_home = fixture.fixture_stats.filter(home_or_away='home')
        players_away = fixture.fixture_stats.filter(home_or_away='away')

    # Create a dict of all HOME players in this fixture, and populate their statistics
    for player in players_home:
        if gameweek.is_current:
            # Loop through the Fixture Stat enum, get the statistics and add to the dict
            for stat_type in FixtureStatIdentifier:
                stat_value = getattr(player.classicleaguelivestandings, stat_type.value, 0)
                add_stat_to_group(home_stats_grouped, stat_type, player.web_name, stat_value)
        else:
            # Add the players statistics to the dict
            stat_type = FixtureStatIdentifier.from_value(player.identifier)
            add_stat_to_group(home_stats_grouped, stat_type, player.player.web_name, player.value)

    # Create a dict of all AWAY players in this fixture, and populate their statistics
    for player in players_away:
        if gameweek.is_current:
            # Loop through the Fixture Stat enum, get the statistics and add to the dict
            for stat_type in FixtureStatIdentifier:
                stat_value = getattr(player.classicleaguelivestandings, stat_type.value, 0)
                add_stat_to_group(away_stats_grouped, stat_type, player.web_name, stat_value)
        else:
            # Add the players statistics to the dict
            stat_type = FixtureStatIdentifier.from_value(player.identifier)
            add_stat_to_group(away_stats_grouped, stat_type, player.player.web_name, player.value)

    # Sort the stats in descending order based on the stat value for both HOME and AWAY
    for stat_type in FixtureStatIdentifier:
        home_stats_grouped[stat_type.value] = sorted(
            home_stats_grouped[stat_type.value],
            key=lambda x: x['value'],
            reverse=True
        )
        away_stats_grouped[stat_type.value] = sorted(
            away_stats_grouped[stat_type.value],
            key=lambda x: x['value'],
            reverse=True
        )

    # Combine the HOME and AWAY stats into one dict
    combined_stats = {}
    for stat_type in FixtureStatIdentifier:
        combined_stats[stat_type.value] = {
            'home': home_stats_grouped[stat_type.value],
            'away': away_stats_grouped[stat_type.value]
        }

    return combined_stats