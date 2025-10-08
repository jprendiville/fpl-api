""" Module for Player urls """

from django.urls import path

from . import views

urlpatterns = [
    path('league-table', views.league_table, name='league-table'),
    path('live-fixtures', views.live_fixtures, name='live-fixtures'),
]
