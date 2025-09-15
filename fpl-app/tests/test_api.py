""" Test suite for urls """

from django.test import SimpleTestCase
from django.urls import resolve, reverse

from fpl.views import denied_page, home, server_error
from manager.views import classic_league_live, classic_league_standings, \
    leagues, managers, progression, reset
from penalties.views import penalties, penalty_create
from players.api.v1.views import PlayerViewSet
from players.views import defence, picker, prediction_evaluator, \
    predictions, price_changes, transfers
from settings.views import refresh_all_data, player_status, \
    recalculate_predictions, refresh_player_data
from teams.views import fdr, league_table, live_fixtures


class TestUrls(SimpleTestCase):
    """ Test suite for urls """

    def test_players_list_url(self):
        """players list endpoint is routed and named correctly"""
        url = reverse('v1:players-list')
        match = resolve(url)
        self.assertEqual(match.view_name, 'v1:players-list')
        # DRF viewsets resolve to a function wrapper; .cls gives the viewset class
        self.assertTrue(issubclass(match.func.cls, PlayerViewSet))

    def test_players_detail_url(self):
        """players detail endpoint is routed and named correctly"""
        url = reverse('v1:players-detail', kwargs={'pk': 123})
        match = resolve(url)
        self.assertEqual(match.view_name, 'v1:players-detail')
        self.assertTrue(issubclass(match.func.cls, PlayerViewSet))

