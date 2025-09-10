import logging

import numpy as np
import pandas as pd
from django.db.models import OuterRef, Q, Subquery, Sum
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler

from common.models.fixture import Fixture
from common.models.season import Season
from fpl.properties.properties import get_properties
from players.models import Player, PlayerHistory, PlayerPrediction, \
    PlayerStatus
from teams.models import TeamPreviousPosition
from utils.sql_utils import get_league_table_by_gameweek

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

properties = get_properties()

def get_predictions(this_gameweek):
    ''' Calculate predictions for a given gameweek using
    RandomForestRegressor.
    What we are doing here is taking all data up to and including gameweek
    x, stripping out gameweek x and calculating predictions using all data
    up to x-1. Then we can compare predictions versus actuals.
    '''
    logger.info("Predicting for game week: %s", this_gameweek.id)

    # Subquery to only select players who have exceeded an average x (configurable) minutes played
    # in all previous games
    minutes_played_threshold = properties.minutes_played * this_gameweek.id
    minutes_played_subquery = PlayerHistory.objects.filter(
        element=OuterRef('element')
    ).values('element').annotate(total_sum=Sum('minutes')).values('total_sum')

    # Subqeury to only select players where their status is equivalent of can_play
    can_play_subquery = PlayerStatus.objects.filter(
        status=OuterRef('player__status')
    ).values('can_play')[:1]


    # Now using the above subquerys, get all players who meet the criteria
    filtered_results = PlayerHistory.objects.annotate(
        total_sum=Subquery(minutes_played_subquery),
        can_play=Subquery(can_play_subquery)
    ).filter(
        total_sum__gt=minutes_played_threshold,
        can_play=True,
        round__lte=this_gameweek.id
    )

    if not filtered_results:
        return
    player_history_data = pd.DataFrame.from_records(
        list(filtered_results.values()))

    # Drop columns
    player_history_data.drop(
        ['fixture', 'transfers_balance', 'selected', 'transfers_in',
         'transfers_out'],
        axis=1, inplace=True)

    # Rename column "round" as it is a reserved word
    player_history_data.rename(columns={"round": "gameweek"}, inplace=True)

    # Convert Boolean to 1/0
    player_history_data.was_home = player_history_data.was_home \
        .replace({True: 1, False: 0})

    # Assign players position/team
    player_history_data = find_player_details(player_history_data)

    # Create a column for the result where 1=Win, 0=Draw, -1=Loss
    player_history_data = find_result(player_history_data)

    # Convert Timestamp to kickoff hour
    player_history_data = find_kickoff_hour(player_history_data)

    # Convert Timestamp to season year
    player_history_data = find_season(player_history_data)
    # Save the season in a variable as we'll use it later
    season = player_history_data.iloc[0]['season']

    # Set the team and opponents position last year
    team_previous_postion = dict(TeamPreviousPosition.objects.filter
                                 (season=season-1).values_list('team',
                                                               'position'))
    player_history_data["team_last_position"] = \
        player_history_data['team'].map(team_previous_postion)
    player_history_data["opponent_last_position"] = \
        player_history_data['opponent_team'].map(team_previous_postion)

    # Apply teams current ranking
    player_history_data = apply_team_ranking(player_history_data, this_gameweek)

    # Add a column to say the game is finished
    player_history_data['finished'] = True

    # Extract out the last gameweek. If we're not evaluating and are predicting for
    # next game week, get the last gameweek as a template and update accordingly
    if this_gameweek.finished is True:
        last_gameweek_data = player_history_data[player_history_data
                                                 .gameweek == this_gameweek.id]
        player_history_data = player_history_data[player_history_data
                                                  .gameweek < this_gameweek.id]
    else:
        last_gameweek_data = set_next_gameweek_data(season, this_gameweek)

    # Give it an index
    player_history_data = player_history_data.set_index(
        player_history_data['first_name'].astype(str) +
        player_history_data['second_name'].astype(str) +
        player_history_data['kickoff_time'].astype('str'))
    player_history_data.drop(['kickoff_time', 'first_name', 'second_name'],
                             axis=1,
                             inplace=True)

    # Select the features we want to use
    feature_list = ['id_x', 'element', 'opponent_team', 'total_points', 'was_home',
                    'team_h_score', 'team_a_score', 'gameweek', 'minutes', 'goals_scored',
                    'assists', 'clean_sheets', 'goals_conceded', 'own_goals',
                    'penalties_saved', 'penalties_missed', 'yellow_cards', 'red_cards',
                    'saves', 'bonus', 'bps', 'influence', 'creativity', 'threat',
                    'ict_index', 'value', 'starts', 'expected_goals', 'expected_assists',
                    'expected_goal_involvements', 'expected_goals_conceded',
                    'element_type', 'team', 'result',
                    'kickoff_hour', 'season', 'team_last_position',
                    'opponent_last_position', 'this_rank',
                    'opponent_rank', 'finished']
    player_history_data = player_history_data[feature_list]
    last_gameweek_data = last_gameweek_data[feature_list]

    # Sort the dataframe by index
    player_history_data = player_history_data.sort_index()


    # We want to work with each element type individually, as grouping player
    # types will give a more accurate reflection
    goalkeeper_history_data = \
        player_history_data[player_history_data['element_type'] == 1]
    defender_history_data = \
        player_history_data[player_history_data['element_type'] == 2]
    midfielder_history_data = \
        player_history_data[player_history_data['element_type'] == 3]
    forward_history_data = \
        player_history_data[player_history_data['element_type'] == 4]

    # calculate stats
    goalkeeper_history_data = calc_stats(goalkeeper_history_data)
    defender_history_data = calc_stats(defender_history_data)
    midfielder_history_data = calc_stats(midfielder_history_data)
    forward_history_data = calc_stats(forward_history_data)

    # get data sets by player type for last gameweek
    goalkeeper_last_gameweek_data = \
        last_gameweek_data[last_gameweek_data['element_type'] == 1]
    defender_last_gameweek_data = \
        last_gameweek_data[last_gameweek_data['element_type'] == 2]
    midfielder_last_gameweek_data = \
        last_gameweek_data[last_gameweek_data['element_type'] == 3]
    forward_last_gameweek_data = \
        last_gameweek_data[last_gameweek_data['element_type'] == 4]

    goalkeeper_data = \
        goalkeeper_history_data.drop_duplicates("element", keep="last")
    defender_data = \
        defender_history_data.drop_duplicates("element", keep="last")
    midfielder_data = \
        midfielder_history_data.drop_duplicates("element", keep="last")
    forward_data = \
        forward_history_data.drop_duplicates("element", keep="last")

    # Predict the different player types
    goalkeeper_data = predict_random_forest('Gameweek ' + str(this_gameweek.id) + ' GOALKEEPERS',
                                            goalkeeper_history_data,
                                            goalkeeper_data,
                                            goalkeeper_last_gameweek_data)
    defender_data = predict_random_forest('Gameweek ' + str(this_gameweek.id) + ' DEFENDERS',
                                          defender_history_data,
                                          defender_data,
                                          defender_last_gameweek_data)
    midfielder_data = predict_random_forest('Gameweek ' + str(this_gameweek.id) + ' MIDFIELDERS',
                                            midfielder_history_data,
                                            midfielder_data,
                                            midfielder_last_gameweek_data)
    forward_data = predict_random_forest('Gameweek ' + str(this_gameweek.id) + ' FORWARDS',
                                         forward_history_data,
                                         forward_data,
                                         forward_last_gameweek_data)

    Season.objects.get_or_create(season=season)

    PlayerPrediction.objects.filter(season=season,
                                    gameweek_id=this_gameweek.id) \
        .delete()
    PlayerPrediction.objects.bulk_create(
        PlayerPrediction(**vals) for vals in
        goalkeeper_data.to_dict('records')
    )
    PlayerPrediction.objects.bulk_create(
        PlayerPrediction(**vals) for vals in
        defender_data.to_dict('records')
    )
    PlayerPrediction.objects.bulk_create(
        PlayerPrediction(**vals) for vals in
        midfielder_data.to_dict('records')
    )
    PlayerPrediction.objects.bulk_create(
        PlayerPrediction(**vals) for vals in
        forward_data.to_dict('records')
    )


def find_result(player_history_data):
    ''' If the team was home, they scored more than the away team or
           the team was away, they scored more than the home team it's a win.
        If the two scores were the same it's a draw.
        Otherwise it's a loss'''
    player_history_data['result'] = player_history_data.apply(lambda row:
                                                              1 if (
                                                                      (row['was_home'] == 1 and row['team_h_score'] > row['team_a_score']) or
                                                                      (row['was_home'] == 0 and row['team_h_score'] < row['team_a_score']))
                                                              else 0 if row['team_h_score'] == row['team_a_score']
                                                              else -1, axis=1)
    return player_history_data


def find_player_details(player_history_data):
    """ Find the players position by looking up the player model """

    # Load all players (id and element_type) to a data frame
    df = pd.DataFrame(list(Player.objects.all()
                           .values('id', 'element_type', 'team', 'first_name', 'second_name')))
    # Merge element type to the history data on
    # player_history_data.element == player.id
    return pd.merge(player_history_data, df,
                    left_on=['element'],
                    right_on=['id'],
                    how='left')


def find_kickoff_hour(player_history_data):
    """ Find the kickoff hour """
    player_history_data["kickoff_hour"] = \
        player_history_data["kickoff_time"].dt.hour
    return player_history_data


def find_season(player_history_data):
    """ Find the season """

    # if the month > 6 add 1 to make it the ending year of the season.
    # eg. if it it 9=September 2022, make it 2023
    player_history_data["season"] = \
        np.where(player_history_data["kickoff_time"].dt.month > 6,
                 player_history_data["kickoff_time"].dt.year + 1,
                 player_history_data["kickoff_time"].dt.year)
    return player_history_data


def predict_random_forest(player_type, train_data, test_data,
                          last_gameweek_data):
    """ Train the model, and do some predictions """

    target = train_data[['total_points', 'gameweek']]
    train_data = train_data.loc[:, train_data.columns != 'total_points']
    test_data = test_data.loc[:, test_data.columns != 'total_points']

    X_train, X_test, y_train, y_test = train_test_split(
        train_data,
        target["total_points"],
        test_size=0.1,
        random_state=0,
    )

    y_train = target["total_points"].loc[y_train.index]

    y_test = target["total_points"].loc[y_test.index]

    model = Pipeline(
        [
            ("imp", SimpleImputer()),
            ("scaler", MinMaxScaler()),
            (
                "model",
                RandomForestRegressor(random_state=0,
                                      max_depth=8,
                                      n_estimators=1000),
            ),
        ]
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    test_data['prediction'] = model.predict(test_data)
    test_data = test_data.merge(last_gameweek_data,
                                left_on=['element'],
                                right_on=['element'],
                                suffixes=('_pred', '_actual'))
    test_data = pd.DataFrame().assign(element=test_data['element'],
                                      gameweek_id=test_data['gameweek_actual'],
                                      season_id=test_data['season_actual'],
                                      total_points=test_data['total_points'],
                                      prediction=test_data['prediction'],
                                      team_h_score=test_data['team_h_score_actual'],
                                      team_a_score=test_data['team_a_score_actual'],
                                      was_home=test_data['was_home_actual'],
                                      opponent_id=test_data['opponent_team_actual'],
                                      player_id=test_data['element'],
                                      finished=test_data['finished_actual'])

    logger.info('%s', player_type)

    return test_data


def get_last_season_pos(team):
    ''' Get where teams finished last season. Return it as a dataframe to add
    to existing data'''
    return pd.DataFrame(pd.DataFrame.from_records(
        TeamPreviousPosition.objects.filter(team_=team)
        .values('position')).values).values


def calc_stats(player_history_data):
    ''' For the selected columns use a rolling average '''
    player_history_data[['goals_conceded', 'own_goals', 'penalties_saved',
                         'penalties_missed', 'saves', 'bonus', 'bps', 'value',
                         'ict_index', 'influence', 'total_points',
                         'creativity', 'threat']] = \
        player_history_data[['goals_conceded', 'own_goals', 'penalties_saved',
                             'penalties_missed', 'saves', 'bonus',
                             'bps', 'value', 'ict_index', 'influence',
                             'total_points', 'creativity', 'threat']].rolling(
            window=properties.rolling_average).mean().fillna(0)

    return player_history_data


def set_next_gameweek_data(season, this_gameweek):
    players = Player.objects.all()
    player_data = [
        {
            'id_x': player.id,
            'element': player.id,
            'opponent_team': 0,
            'total_points': player.total_points,
            'was_home': False,
            'team_h_score': 0,
            'team_a_score': 0,
            'gameweek': this_gameweek.id,
            'minutes': 0,
            'goals_scored': 0,
            'assists': 0,
            'clean_sheets': 0,
            'goals_conceded': 0,
            'own_goals': 0,
            'penalties_saved': 0,
            'penalties_missed': 0,
            'yellow_cards': 0,
            'red_cards': 0,
            'saves': 0,
            'bonus': 0,
            'bps': 0,
            'influence': player.influence,
            'creativity': player.creativity,
            'threat': player.threat,
            'ict_index': player.ict_index,
            'value': player.now_cost,
            'starts': player.starts,
            'expected_goals': player.expected_goals,
            'expected_assists': player.expected_assists,
            'expected_goal_involvements': player.expected_goal_involvements,
            'expected_goals_conceded': player.expected_goals_conceded,
            'player_id': player.id,
            'opponent_id': 0,
            'id_y': 0,
            'element_type': player.element_type,
            'team': player.team,
            'first_name': player.first_name,
            'second_name': player.second_name,
            'result': 0,
            'season': season,
            'team_last_position': 0,
            'opponent_last_position': 0,
            'finished': False
        }
        for player in players
    ]

    player_data_df = pd.DataFrame(player_data)

    def get_opponent_and_home_flag(row):
        team_id = row['team']
        gameweek = row['gameweek']
        fixtures = Fixture.objects.filter(Q(event=gameweek) & (Q(team_home=team_id) | Q(team_away=team_id)))

        fixture_data = []
        for fixture in fixtures:
            opponent_team_id = fixture.team_away.id if fixture.team_home.id == team_id else fixture.team_home.id
            is_home = fixture.team_home.id == team_id
            kickoff_time = fixture.kickoff_time
            fixture_data.append({'opponent_team': opponent_team_id, 'was_home': is_home, 'kickoff_time': kickoff_time})

        return fixture_data


    expanded_rows = []
    for index, row in player_data_df.iterrows():
        fixtures_data = get_opponent_and_home_flag(row)
        for fixture in fixtures_data:
            new_row = row.copy()
            new_row['opponent_team'] = fixture['opponent_team']
            new_row['was_home'] = fixture['was_home']
            new_row['kickoff_time'] = fixture['kickoff_time']
            expanded_rows.append(new_row)

    player_data_df = pd.DataFrame(expanded_rows)

    player_data_df = find_kickoff_hour(player_data_df)

    player_data_df = apply_team_ranking(player_data_df, this_gameweek)

    return player_data_df


def apply_team_ranking(player_history_data, gameweek):
    # Get teams position as of this gameweek
    team_position = get_league_table_by_gameweek(gameweek.id, None)
    team_positon_df = pd.DataFrame(team_position)
    # Adjust rank, losses, goals_against
    team_positon_df[['rank', 'losses', 'goals_against']] = team_positon_df[['rank', 'losses', 'goals_against']] * -1

    # Set this teams position
    this_team_positon_df = team_positon_df.rename(columns=lambda x: 'this_' + x)
    this_team_positon_df = this_team_positon_df[['this_id', 'this_rank']]
    player_history_data = pd.merge(player_history_data, this_team_positon_df, left_on='team', right_on='this_id', how='left')

    # Set the opponents position
    opponent_team_positon_df = team_positon_df.rename(columns=lambda x: 'opponent_' + x)
    opponent_team_positon_df = opponent_team_positon_df[['opponent_id', 'opponent_rank']]
    player_history_data = pd.merge(player_history_data, opponent_team_positon_df, left_on='opponent_team', right_on='opponent_id', how='left')

    return player_history_data