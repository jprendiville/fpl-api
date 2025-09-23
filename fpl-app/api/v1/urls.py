from django.urls import path, include
from rest_framework.routers import DefaultRouter
from players.api.v1.views import DefenceViewSet, ElementTypeViewSet, \
    PlayerHistoryViewSet, PlayerViewSet
from teams.api.v1.teams import TeamViewSet

router = DefaultRouter()
router.register(r"players", PlayerViewSet, basename="players")
router.register(r"defence", DefenceViewSet, basename="defence")
router.register(r"teams", TeamViewSet, basename="teams")
router.register(r"element-types", TeamViewSet, basename="element-types")
player_history_list = PlayerHistoryViewSet.as_view({'get': 'list'})

urlpatterns = [
    path('', include(router.urls)),
    path('players/<int:player_id>/player-history/', player_history_list, name='player-history-by-player'),
]
