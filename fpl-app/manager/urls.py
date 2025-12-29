""" Module for Manager urls """

from django.urls import path

from . import views

urlpatterns = [
    path('league/<int:id>/manager/<int:manager_id>',
         views.classic_league_standings, name='league'),
    path('live/<int:id>/manager/<int:manager_id>',
         views.classic_league_live, name='live'),
]
