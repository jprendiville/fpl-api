""" Module for Manager urls """

from django.urls import path

from . import views

urlpatterns = [
    path('managers', views.managers, name='managers'),
    path('reset', views.reset, name='reset'),
    path('leagues/<int:manager_id>', views.leagues, name='leagues'),
    path('league/<int:id>/manager/<int:manager_id>',
         views.classic_league_standings, name='league'),
    path('live/<int:id>/manager/<int:manager_id>',
         views.classic_league_live, name='live'),
    path('progression/<int:id>', views.progression, name='progression'),
    path('reload-league/<int:id>/<int:manager_id>', views.reload_league, name='reload-league'),
]
