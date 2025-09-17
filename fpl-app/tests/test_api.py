""" Test suite for urls """

from django.test import SimpleTestCase
from django.urls import resolve, reverse

from players.api.v1.views import DefenceViewSet, PlayerViewSet


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

    def test_defence_list_url(self):
        """defence  list endpoint is routed and named correctly"""
        url = reverse('v1:defence-list')
        match = resolve(url)
        self.assertEqual(match.view_name, 'v1:defence-list')
        # DRF viewsets resolve to a function wrapper; .cls gives the viewset class
        self.assertTrue(issubclass(match.func.cls, DefenceViewSet))

    def test_defence_detail_url(self):
        """defence detail endpoint is routed and named correctly"""
        url = reverse('v1:defence-detail', kwargs={'pk': 123})
        match = resolve(url)
        self.assertEqual(match.view_name, 'v1:defence-detail')
        self.assertTrue(issubclass(match.func.cls, DefenceViewSet))