from django.urls import path, include
from rest_framework.routers import DefaultRouter

from common.api.v1.views import EventViewSet
from manager.api.v1.views import ClassicLeagueReloadView, \
    LeagueProgressionView, ManagersViewSet
from players.api.v1.views import DefenceViewSet, \
    PlayerHistoryViewSet, PlayerViewSet, TransfersInViewSet, \
    TransfersOutViewSet
from teams.api.v1.views import FdrViewSet, LeagueTableViewSet, TeamViewSet

router = DefaultRouter()
router.register(r"players", PlayerViewSet, basename="players")
router.register(r"defence", DefenceViewSet, basename="defence")
router.register("transfers-in", TransfersInViewSet, basename="transfers-in")
router.register("transfers-out", TransfersOutViewSet, basename="transfers-out")
router.register(r"teams", TeamViewSet, basename="teams")
router.register(r"element-types", TeamViewSet, basename="element-types")
router.register(r"events", EventViewSet, basename="event")
router.register(r"fdr", FdrViewSet, basename="fdr")
router.register(r"league-table", LeagueTableViewSet, basename="league-table")
router.register(r"managers", ManagersViewSet, basename="managers"),
player_history_list = PlayerHistoryViewSet.as_view({'get': 'list'})

urlpatterns = [
    path('', include(router.urls)),
    path('players/<int:player_id>/player-history/', player_history_list, name='player-history-by-player'),
    path("reload-league/<int:league_id>/", ClassicLeagueReloadView.as_view(), name="reload-league"),
    path("league-progression/<int:league_id>/", LeagueProgressionView.as_view(), name="league-progression"),


]
