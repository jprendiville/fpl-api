from rest_framework import viewsets, filters as drf_filters
from django_filters.rest_framework import DjangoFilterBackend
from teams.models import Team
from .serializers import TeamMiniSerializer

class TeamViewSet(viewsets.ReadOnlyModelViewSet):
    """
    /api/v1/teams/ (list)
    /api/v1/teams/{id}/ (detail)
    """
    queryset = Team.objects.all().order_by("short_name")
    serializer_class = TeamMiniSerializer

    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    pagination_class = None
