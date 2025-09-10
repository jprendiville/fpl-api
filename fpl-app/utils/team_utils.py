from utils.sql_utils import get_league_table_by_gameweek


def find_team_position(gameweek, team):
    league_table = get_league_table_by_gameweek(gameweek, team)
    return next((item for item in league_table if item.get('id') == team), None)