""" Test suite for models """
from enum import Enum

from django.db.models import Q
from django.test import TestCase
from django.utils import timezone

from common.models.event_status import EventStatus
from common.utils import get_next_n_games_fdr
from manager.models import ClassicLeague, ClassicLeagueStandings, History,\
    Information, ManagerTeam, Pick
from manager.models.classic_league_live_standings import \
    ClassicLeagueLiveStandings
from penalties.models.penalty import Penalty
from players.models import ElementType, Event, Fixture, Player, PlayerHistory, \
    PlayerPrediction, PlayerStatus
from common.models.season import Season
from teams.models import Team


class PlayerStatusEnum(Enum):
    AVAILABLE = 'a'
    UNAVAILABLE = 'u'

class TestModels(TestCase):
    """ Test suite for models """

    def setUp(self):
        """ Setup the test data """
        self.season = Season.objects.create(
            season=2023
        )
        self.event_previous = Event.objects.create(
            id=2,
            name='Gameweek 2',
            is_previous=True,
            chip_plays=[],
            deadline_time=timezone.now()
        )
        self.event_current = Event.objects.create(
            id=3,
            name='Gameweek 3',
            is_current=True,
            chip_plays=[],
            deadline_time=timezone.now()
        )
        self.event_next = Event.objects.create(
            id=4,
            name='Gameweek 4',
            is_next=True,
            chip_plays=[],
            deadline_time=timezone.now()
        )

        self.event_status = EventStatus.objects.create(
            id = 1,
            bonus_added=True,
            date = timezone.now().date(),
            event = 3,
            gameweek = self.event_current
        )

        self.home_team = Team.objects.create(
            id=1,
            name='Home Team',
            short_name='HT'
        )
        self.away_team = Team.objects.create(
            id=2,
            name='Away Team',
            short_name='AT'
        )
        self.multiple_team_games = Team.objects.create(
            id=3,
            name='Multiple Games',
            short_name='MG'

        )
        self.team_no_games = Team.objects.create(
            id=4,
            name='No games',
            short_name='NG'
        )

        self.fpl_fixture = Fixture.objects.create(
            id=1,
            event=self.event_previous.id,
            team_h=self.home_team.id,
            team_a=self.away_team.id,
            team_h_difficulty=3,
            team_a_difficulty=2,
            team_home=self.home_team,
            team_away=self.away_team,
            kickoff_time=timezone.now()
        )

        self.fpl_multiple_fixture1 = Fixture.objects.create(
            id=2,
            event=self.event_previous.id,
            team_h=self.multiple_team_games.id,
            team_a=self.away_team.id,
            team_h_difficulty=2,
            team_a_difficulty=4,
            team_home=self.multiple_team_games,
            team_away=self.away_team,
            kickoff_time=timezone.now()
        )

        self.fpl_multiple_fixture2 = Fixture.objects.create(
            id=3,
            event=self.event_current.id,
            team_h=self.home_team.id,
            team_a=self.multiple_team_games.id,
            team_h_difficulty=4,
            team_a_difficulty=4,
            team_home=self.home_team,
            team_away=self.multiple_team_games,
            kickoff_time=timezone.now()
        )

        self.element_type = ElementType.objects.create(
            id=100,
            plural_name='Midfielders',
            plural_name_short='MID',
            singular_name='Midfielder',
            singular_name_short='MID',
            squad_select=0,
            squad_min_play=0,
            squad_max_play=0,
            ui_shirt_specific=False,
            sub_positions_locked=False,
            element_count=100,
        )

        self.player1 = Player.objects.create(
            id=100001,
            first_name='First name 1',
            second_name='Second name 1',
            web_name='Web name 1',
            player_team=self.home_team,
            player_type=self.element_type
        )
        self.player2 = Player.objects.create(
            id=100002,
            first_name='First name 2',
            second_name='Second name 2',
            web_name='Web name 2',
            player_team=self.home_team,
            player_type=self.element_type
        )
        self.player3 = Player.objects.create(
            id=100003,
            first_name='First name 3',
            second_name='Second name 3',
            web_name='Web name 3',
            player_team=self.home_team,
            player_type=self.element_type
        )
        self.player1_history1 = PlayerHistory.objects.create(
            id=200001,
            element=self.player1.id,
            fixture=self.fpl_multiple_fixture1.event,
            player=self.player1,
            opponent=self.away_team
        )
        self.player1_history2 = PlayerHistory.objects.create(
            id=200002,
            element=self.player1.id,
            fixture=self.fpl_multiple_fixture2.event,
            opponent=self.away_team
        )

        self.penalty = Penalty.objects.create(
            id=1,
            team=self.home_team,
            taker=self.player1,
            goalkeeper=self.player2,
            gameweek=self.event_current,
            venue=Penalty.Venue.HOME,
            result=Penalty.Result.SCORED,
            var_awarded=False
        )

        self.manager = ManagerTeam.objects.create(
            id=123,
            last_updated_gameweek=self.event_current.id
        )
        self.pick = Pick.objects.create(
            id=self.player1.id,
            position=3,
            player=self.player1,
            manager=self.manager
        )
        self.information = Information.objects.create(
            id=123,
            player_first_name='Man',
            player_last_name='ager',
            name='Team name'
        )
        self.history = History.objects.create(
            event=self.event_current.id,
            points=23,
            total_points=123,
            manager=self.manager
        )
        self.classic_league = ClassicLeague.objects.create(
            league_id=123,
            manager=self.manager,
            name="League Name"
        )
        self.classic_league_standings = ClassicLeagueStandings.objects.create(
            league_id=123,
            player_name=self.information.player_first_name + ' ' +
                        self.information.player_last_name,
            rank=1
        )
        self.player_prediction = PlayerPrediction.objects.create(
            element=self.player1.id,
            season=self.season,
            gameweek=self.event_current,
            total_points=8,
            prediction=6.167,
            team_h_score=3,
            team_a_score=0,
            was_home=1,
            opponent=self.away_team,
            player=self.player1
        )
        self.live_points = ClassicLeagueLiveStandings.objects.create(
            player=self.player1,
            minutes=65,
            goals_scored=1,
            total_points=8,
            bonus=2
        )

        self.player_available = PlayerStatus.objects.create(
            status=PlayerStatusEnum.AVAILABLE.value,
            description='available',
            can_play=True
        )
        self.player_unavailable = PlayerStatus.objects.create(
            status=PlayerStatusEnum.UNAVAILABLE.value,
            description='unavailable',
            can_play=False
        )

    def test_team(self):
        """ Test that a team can be created and is valid """
        assert self.home_team.short_name == 'HT'

    def test_multiple_games(self):
        """ Testing multiple games """
        # We have setup one team (multiple_team_games) to play the other two.
        # Test that a team can have multiple games in an event.
        assert len(get_next_n_games_fdr(self.multiple_team_games, self.event_current, 100)) == 2

    def test_team_fdr_next_games(self):
        """ Testing FDR next games """
        home_games = get_next_n_games_fdr(self.home_team, self.event_current, 100)
        team_no_games = get_next_n_games_fdr(self.team_no_games, self.event_current, 100)

        # We expect exactly one fixture for home_team
        assert len([g for g in home_games if g.get("opponents")]) == 1
    
        # We expect no fixtures for team_no_games
        assert all(g.get("opponents") is None for g in team_no_games)


    def test_element_type(self):
        """ Test that an element type can be created and is valid """
        results = ElementType.objects.filter(Q(id=self.element_type.id))
        assert self.element_type in results
        assert self.element_type.plural_name_short == 'MID'
        assert self.element_type.plural_name == 'Midfielders'
        assert self.element_type.ui_shirt_specific is False
        assert self.element_type.element_count == 100

    def test_player(self):
        """ Test that a player can be created and is valid """
        # Run a filter over the set to retrieve player1 and player3
        results = Player.objects.filter(Q(id=self.player1.id) | Q(id=self.player3.id))
        # Check if the player is in the result
        assert self.player1 in results
        assert self.player2 not in results
        assert self.player3 in results

    def test_player_history(self):
        """ Test that a manager history can be created and is valid """
        results = Player.objects.filter(Q(id=self.player1.id))
        assert self.player1_history1 in results.get().playerhistory_set.all()

    def test_penalty(self):
        """ Test that a penalty can be created and is valid """
        results = Penalty.objects.filter(Q(id=self.penalty.id))
        assert self.penalty in results

    def test_manager(self):
        """ Test that a manager can be created and is valid """
        manager_results = ManagerTeam.objects.filter(Q(id=self.manager.id))
        pick_results = Pick.objects.filter(Q(manager_id=self.manager.id))
        information_results = Information.objects.filter(Q(id=self.manager.id))
        history_results = History.objects.filter(Q(manager_id=self.manager.id))
        classic_league_results = ClassicLeague.objects.filter(Q(manager_id=self.manager.id))
        classic_league_standings_results = \
            ClassicLeagueStandings.objects.filter(Q(league_id=self.classic_league_standings.league_id))

        assert self.manager in manager_results
        assert self.pick in pick_results
        assert self.information in information_results
        assert self.history in history_results
        assert self.classic_league in classic_league_results
        assert self.classic_league_standings in classic_league_standings_results


    def test_player_prediction(self):
        """ Test that a player prediction can be created and is valid """
        results = PlayerPrediction.objects.filter(Q(player_id=self.player1.id))
        assert self.player_prediction in results

    def test_player_livepoints(self):
        """ Test that a player prediction can be created and is valid """
        results = ClassicLeagueLiveStandings.objects.filter(Q(player_id=self.player1.id))
        assert self.live_points in results

    def test_event_status(self):
        """ Test that a event status can be created and is valid """
        results = EventStatus.objects.filter(Q(id=self.event_status.id))
        assert self.event_status in results

    def test_player_available(self):
        """ Test that a player status can be created and is valid """
        results = PlayerStatus.objects.filter(Q(status=PlayerStatusEnum.AVAILABLE.value))
        assert self.player_available in results

    def test_player_unavailable(self):
        """ Test that a player status can be created and is valid """
        results = PlayerStatus.objects.filter(Q(status=PlayerStatusEnum.UNAVAILABLE.value))
        assert self.player_unavailable in results