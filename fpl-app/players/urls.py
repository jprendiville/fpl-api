""" Module for Player urls """

from django.urls import path

from . import views

urlpatterns = [
    path('transfers', views.transfers, name='transfers'),
    path('price-changes', views.price_changes, name='price-changes'),
    path('picker', views.picker, name='picker'),
    path('predictions', views.predictions, name='predictions'),
    path('prediction-evaluator', views.prediction_evaluator, name='prediction-evaluator'),
    path('player-history/<int:pk>', views.PlayerHistoryView.as_view(), name='player-history'),
    path('player-prediction-history/<int:pk>', views.PlayerPredictionHistoryView.as_view(),
         name='player-prediction-history'),
]
