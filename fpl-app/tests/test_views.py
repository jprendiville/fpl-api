""" Test suite for views """

from django.test import Client, TestCase
from django.urls import reverse
from datetime import datetime, timezone

from common.models.last_updated import LastUpdated
from manager.models import ClassicLeague, ClassicLeagueStandings, Information,\
    ManagerTeam, Pick
from penalties.models.penalty import Penalty
from players.models import ElementType, Event, Fixture, Player
from teams.models import Team


class TestViews(TestCase):
    """ Test suite for views """

    def setUp(self):
        """ This function sets up the test data """
        self.client = Client()
        self.last_updated = LastUpdated.objects.create(
            fpl_data=datetime.now(timezone.utc),
            live_data=datetime.now(timezone.utc),
            fixture_data=datetime.now(timezone.utc),
            prediction_data=datetime.now(timezone.utc)
        )
        self.event_previous = Event.objects.create(
            id=1,
            name='Gameweek 1',
            is_previous=True,
            is_current=False,
            finished=False,
            is_next=False,
            deadline_time=datetime.now(timezone.utc)
        )
        self.event_current = Event.objects.create(
            id=2,
            name='Gameweek 2',
            is_previous=False,
            is_current=True,
            finished=False,
            is_next=False,
            deadline_time=datetime.now(timezone.utc)
        )
        self.event_next = Event.objects.create(
            id=3,
            name='Gameweek 3',
            is_previous=False,
            is_current=False,
            finished=False,
            is_next=True,
            deadline_time=datetime.now(timezone.utc)
        )
        self.event_last_completed = Event.objects.create(
            id=4,
            name='Gameweek 4',
            is_previous=True,
            is_current=False,
            finished=True,
            is_next=False,
            deadline_time=datetime.now(timezone.utc)
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
        self.fixture = Fixture.objects.create(
            id=1,
            event=self.event_next.id,
            team_h=self.home_team.id,
            team_a=self.away_team.id,
            kickoff_time=datetime.now(timezone.utc)
        )
        self.manager = ManagerTeam.objects.create(
            id=123,
            last_updated_gameweek=self.event_current.id,
        )
        self.information = Information.objects.create(
            id=123,
            player_first_name='John',
            player_last_name='Doe'
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
            sub_positions_locked=[12],
            element_count=100
        )
        # Create 15 players
        for i in range(1, 16):
            self.player = Player.objects.create(
                id=100000 + i,
                first_name='First name ' + str(i),
                second_name='Second name ' + str(i),
                web_name='Web name ' + str(i),
                now_cost=5.0 + i/5,
                total_points=40 + i,
                points_per_game=3 + i,
                minutes=70 + i,
                player_team=self.home_team,
                player_type=self.element_type,
                cost_change_event=1,
                ep_next=5
            )
            setattr(self, f"player{i}", self.player)

        # Create 15 players for the manager
        for i in range(1, 16):
            player = getattr(self, f"player{i}")
            Pick.objects.create(
                gameweek=self.event_current.id,
                player=player,
                manager=self.manager,
                multiplier=1
            )

        self.classic_league = ClassicLeague.objects.create(
            league_id=123,
            manager=self.manager,
            name="League Name"
        )
        self.classic_league_standings = ClassicLeagueStandings.objects.create(
            league_id=123,
            gameweek=self.event_current,
            entry=self.manager.id,
            player_name=self.information.player_first_name + ' '
                        + self.information.player_last_name,
            rank=1,
            total=101,
            last_updated=datetime.now(timezone.utc)
        )

        self.classic_league_private = ClassicLeague.objects.create(
            league_id=456,
            manager=self.manager,
            name="Private League",
            league_type='x'
        )
        self.classic_league_standings_private = ClassicLeagueStandings.objects.create(
            league_id=456,
            gameweek=self.event_last_completed,
            entry=self.manager.id,
            player_name=self.information.player_first_name + ' '
                        + self.information.player_last_name,
            rank=1,
            total=201,
            last_updated=datetime.now(timezone.utc)
        )

        self.classic_league_not_private = ClassicLeague.objects.create(
            league_id=789,
            manager=self.manager,
            name="Non-Private League",
            league_type='c'
        )
        self.classic_league_not_private_standings = ClassicLeagueStandings.objects.create(
            league_id=789,
            gameweek=self.event_last_completed,
            entry=self.manager.id,
            player_name=self.information.player_first_name + ' '
                        + self.information.player_last_name,
            rank=1,
            total=301,
            last_updated=datetime.now(timezone.utc)
        )


        self.penalty = Penalty.objects.create(
            id=1,
            team=self.home_team,
            taker=self.player,
            goalkeeper=self.player,
            gameweek=self.event_current,
            venue=Penalty.Venue.HOME,
            result=Penalty.Result.SCORED,
            var_awarded=False
        )

    def test_players(self):
        """ Test the players view is valid """
        response = self.client.get(reverse('players'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'players.html')

    def test_fdr(self):
        """ Test the team fdr view is valid """
        response = self.client.get(reverse('fdr'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'fdr.html')

    def test_league_table(self):
        """ Test the team fdr view is valid """
        response = self.client.get(reverse('league-table'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'league-table.html')

    def test_live_fixtures(self):
        """ Test that the live fixtures view is valid """
        response = self.client.get(reverse('live-fixtures'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'live-fixtures.html')

    def test_penalty(self):
        """ Test the penalties view is valid """
        response = self.client.get(reverse('penalties'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'penalties.html')

    def test_penalty_create(self):
        """ Test the penalty create view is valid """
        response = self.client.get(reverse('create'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create.html')

    def test_manager(self):
        """ Test the manager view is valid """
        response = self.client.get(reverse('managers'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'managers.html')

    def test_manager_reset(self):
        """ Test the manager reset view is valid """
        response = self.client.get(reverse('reset'))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/managers/managers')

    def test_manager_leagues(self):
        """ Test the manager leagues view is valid """
        response = self.client.get(reverse('leagues', args=[123]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'leagues.html')

    def test_league_progression(self):
        """ Test the manager leagues view is valid """
        response = self.client.get(reverse('progression', args=[123]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'progression.html')

    def test_transfers(self):
        """ Test the transfers view is valid """
        response = self.client.get(reverse('transfers'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'transfers.html')

    def test_picker(self):
        """ Test the picker view is valid """
        response = self.client.get(reverse('picker'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'picker.html')


    def test_defence(self):
        """ Test the defence view is valid """
        response = self.client.get(reverse('defence'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'defence.html')


    def test_price_changes(self):
        """ Test the price change view is valid """
        response = self.client.get(reverse('price-changes'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'price-changes.html')

    def test_prediction(self):
        """ Test the price change view is valid """
        response = self.client.get(reverse('predictions'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'predictions.html')

    def test_prediction_evaluator(self):
        """ Test the prediction view is valid """
        response = self.client.get(reverse('prediction-evaluator'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'prediction-evaluator.html')

    def test_private_league(self):
        """ Test that a private league view is valid """
        response = self.client.get(
            reverse('league',
            args=[self.classic_league_private.league_id, self.manager.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'league-standings.html')


    def test_not_private_league(self):
        """ Test that a private league view is valid """
        response = self.client.get(
            reverse('league',
            args=[self.classic_league_not_private.league_id, self.manager.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'denied-page.html')


    def test_league_livepoints(self):
        """ Test that a live points view is valid """
        response = self.client.get(
            reverse('live',
                    args=[self.classic_league.league_id, self.manager.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'league-live.html')

    def test_player_status(self):
        """ Test that a player status view is valid """
        response = self.client.get(reverse('player-status'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'player-status.html')

    def test_server_error(self):
        """ Test that the server error view is valid """
        response = self.client.get(reverse('server-error'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'server-error.html')
