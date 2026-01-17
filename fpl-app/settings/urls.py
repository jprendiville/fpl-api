""" Module for Player urls """

from django.urls import path

from . import views

urlpatterns = [
    path('refresh-all-data', views.refresh_all_data, name='refresh-all-data'),
    path('refresh-player-data', views.refresh_player_data, name='refresh-player-data'),
    path('recalculate-predictions', views.recalculate_predictions, {'recalculate_all': False}, name='recalculate-predictions'),
    path('recalculate-all-predictions', views.recalculate_predictions, {'recalculate_all': True}, name='recalculate-all-predictions'),
]
