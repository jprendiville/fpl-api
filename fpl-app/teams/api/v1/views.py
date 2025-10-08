from rest_framework import viewsets, filters as drf_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response

from common.utils import get_current_gameweek
from teams.models import Team
from utils.sql_utils import get_league_table_by_gameweek
from .serializers import LeagueTableSerializer, TeamFdrSerializer, \
    TeamSerializer

class TeamViewSet(viewsets.ReadOnlyModelViewSet):
    """
    /api/v1/teams/ (list)
    /api/v1/teams/{id}/ (detail)
    """
    queryset = Team.objects.all().order_by("short_name")
    serializer_class = TeamSerializer

    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    pagination_class = None


class FdrViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Endpoints:
      - GET /api/v1/fdr/         (list of teams with next_games)
      - GET /api/v1/fdr/{id}/    (single team with next_games)
    """
    queryset = Team.objects.all().order_by("name")
    serializer_class = TeamFdrSerializer
    pagination_class = None

class LeagueTableViewSet(viewsets.ViewSet):
    """
    Endpoints:
      - GET /api/v1/league-table/
      - GET /api/v1/league-table/?gameweek=5
      - GET /api/v1/league-table/?event_date=2025-09-01
    """

    def list(self, request, *args, **kwargs):
        gameweek = request.query_params.get("gameweek")
        event_date = request.query_params.get("event_date")

        if gameweek:
            league_table = get_league_table_by_gameweek(int(gameweek), None)
        elif event_date:
            league_table = get_league_table_by_gameweek(None, event_date)
        else:
            league_table = get_league_table_by_gameweek(get_current_gameweek().id, None)

        serializer = LeagueTableSerializer(league_table, many=True)
        return Response(serializer.data)