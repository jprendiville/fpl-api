from rest_framework import viewsets, filters as drf_filters
from django_filters.rest_framework import DjangoFilterBackend
from teams.models import Team
from .serializers import TeamFdrSerializer, TeamSerializer

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