""" Test suite for urls """

from django.test import SimpleTestCase
from django.urls import resolve, reverse

from fpl.views import denied_page, home, server_error
from manager.views import classic_league_live, classic_league_standings, \
    leagues, managers, progression, reset
from penalties.views import penalties, penalty_create
from players.views import defence, picker, players, prediction_evaluator, \
    predictions, price_changes, transfers
from settings.views import refresh_all_data, player_status, \
    recalculate_predictions, refresh_player_data
from teams.views import fdr, league_table, live_fixtures


class TestUrls(SimpleTestCase):
    """ Test suite for urls """

    def test_home(self):
        """ Test that the home url is valid """
        url = reverse('home')
        self.assertEqual(resolve(url).func, home)

    def test_players(self):
        """ Test that the players url is valid """
        url = reverse('players')
        self.assertEqual(resolve(url).func, players)

    def test_fdr(self):
        """ Test that the team fdr url is valid """
        url = reverse('fdr')
        self.assertEqual(resolve(url).func, fdr)

    def test_league_table(self):
        """ Test that the team fdr url is valid """
        url = reverse('league-table')
        self.assertEqual(resolve(url).func, league_table)

    def test_live_fixtures(self):
        """ Test live fixtures url is valid """
        url = reverse('live-fixtures')
        self.assertEqual(resolve(url).func, live_fixtures)

    def test_penalty(self):
        """ Test that the penalties url is valid """
        url = reverse('penalties')
        self.assertEqual(resolve(url).func, penalties)

    def test_penalty_create(self):
        """ Test that the penalty create url is valid """
        url = reverse('create')
        self.assertEqual(resolve(url).func, penalty_create)

    def test_manager_team(self):
        """ Test that the manager team url is valid """
        url = reverse('managers')
        self.assertEqual(resolve(url).func, managers)

    def test_manager_reset(self):
        """ Test that the manager reset url is valid """
        url = reverse('reset')
        self.assertEqual(resolve(url).func, reset)

    def test_manager_leagues(self):
        """ Test that the manager url is valid """
        url = reverse('leagues', args=[123])
        self.assertEqual(resolve(url).func, leagues)

    def test_manager_leagues_standings(self):
        """ Test that the manager leagues url is valid """
        url = reverse('league', args=[123, 456])
        self.assertEqual(resolve(url).func, classic_league_standings)

    def test_transfers(self):
        """ Test that the transfers url is valid """
        url = reverse('transfers')
        self.assertEqual(resolve(url).func, transfers)

    def test_picker(self):
        """ Test that the picker url is valid """
        url = reverse('picker')
        self.assertEqual(resolve(url).func, picker)

    def test_defence(self):
        """ Test that the picker url is valid """
        url = reverse('defence')
        self.assertEqual(resolve(url).func, defence)

    def test_price_change(self):
        """ Test that the price change url is valid """
        url = reverse('price-changes')
        self.assertEqual(resolve(url).func, price_changes)

    def test_prediction(self):
        """ Test that the prediction url is valid """
        url = reverse('predictions')
        self.assertEqual(resolve(url).func, predictions)

    def test_manager_livepoints(self):
        """ Test that the manager leagues url is valid """
        url = reverse('live', args=[123, 456])
        self.assertEqual(resolve(url).func, classic_league_live)

    def test_prediction_evaluator(self):
        """ Test that the prediction evaluator url is valid """
        url = reverse('prediction-evaluator')
        self.assertEqual(resolve(url).func, prediction_evaluator)

    def test_league_progression(self):
        """ Test that the league progression url is valid """
        url = reverse('progression', args=[123])
        self.assertEqual(resolve(url).func, progression)

    def test_data_refresh(self):
        """ Test that the data refresh url is valid """
        url = reverse('refresh-all-data')
        self.assertEqual(resolve(url).func, refresh_all_data)

    def test_player_refresh(self):
        """ Test that the player data refresh url is valid """
        url = reverse('refresh-player-data')
        self.assertEqual(resolve(url).func, refresh_player_data)

    def test_recalculate_predictions(self):
        """ Test that the rebuild predictions url is valid """
        url = reverse('recalculate-predictions')
        self.assertEqual(resolve(url).func, recalculate_predictions)

    def test_player_status(self):
        """ Test that the player status url is valid """
        url = reverse('player-status')
        self.assertEqual(resolve(url).func, player_status)

    def test_access_denied(self):
        """ Test that the access denied url is valid """
        url = reverse('access-denied')
        self.assertEqual(resolve(url).func, denied_page)

    def test_server_error(self):
        """ Test that the server error url is valid """
        url = reverse('server-error')
        self.assertEqual(resolve(url).func, server_error)
