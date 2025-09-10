from django.db import connection


def get_league_table_by_gameweek(gameweek, event_date):
    """
    This is a customer SQL to get the league table by gameweek
    :param gameweek:
    :return: Dict of league table orderded by rank
    """
    sql = """
        SELECT
            ROW_NUMBER() OVER (ORDER BY sum(points) DESC) AS rank,
            id,
            name,
            SUM(played) AS played,
            SUM(wins) AS wins,
            SUM(draws) AS draws,
            SUM(losses) AS losses,
            SUM(goals_for) as goals_for,
            SUM(goals_against) as goals_against,
            SUM(goal_difference) as goal_difference,
            SUM(points) AS total_points
        FROM (
            SELECT
                pt.id,
                pt.name,
                CASE
                    WHEN team_h = pt.id OR team_a = pt.id THEN 1
                    ELSE 0
                END AS played,
                CASE
                    WHEN team_h = pt.id AND team_h_score > team_a_score THEN 1
                    WHEN team_a = pt.id AND team_a_score > team_h_score THEN 1
                    ELSE 0
                END AS wins,
                CASE
                    WHEN (team_h = pt.id OR team_a = pt.id) AND team_h_score = team_a_score THEN 1
                    ELSE 0
                END AS draws,
                CASE
                    WHEN team_h = pt.id AND team_h_score < team_a_score THEN 1
                    WHEN team_a = pt.id AND team_a_score < team_h_score THEN 1
                    ELSE 0
                END AS losses,
                CASE
                    WHEN team_h = pt.id THEN team_h_score ELSE team_a_score
                END AS goals_for,
                CASE
                    WHEN team_h = pt.id THEN team_a_score ELSE team_h_score
                END AS goals_against,
                CASE
                    WHEN team_h = pt.id THEN team_h_score - team_a_score
                    WHEN team_a = pt.id THEN team_a_score - team_h_score
                    ELSE 0
                END AS goal_difference, 
                CASE
                    WHEN team_h = pt.id AND team_h_score > team_a_score THEN 3
                    WHEN team_a = pt.id AND team_a_score > team_h_score THEN 3
                    WHEN team_h = pt.id AND team_h_score < team_a_score THEN 0
                    WHEN team_a = pt.id AND team_a_score < team_h_score THEN 0
                    WHEN (team_h = pt.id OR team_a = pt.id) AND team_h_score = team_a_score THEN 1
                END AS points
            FROM teams_team pt
            JOIN common_fixture ON (team_h = pt.id OR team_a = pt.id)
            WHERE finished = True AND (event <= %s OR DATE(kickoff_time) <= %s)
        ) AS results
        GROUP BY id, name
        ORDER BY total_points DESC, goal_difference DESC;
        """
    with connection.cursor() as cursor:
        cursor.execute(sql, [gameweek, event_date])
        columns = [col[0] for col in cursor.description]
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]
