from rest_framework import filters as drf_filters
from django_filters.rest_framework import DjangoFilterBackend, filters
from rest_framework.viewsets import ReadOnlyModelViewSet

from players.models import Player
from .serializers import PlayerDefenceSerializer, PlayerListSerializer
from .filters import OrderingFilterCompat, PlayerFilter

class PlayerViewSet(ReadOnlyModelViewSet):
    """
    Endpoints:
      - GET /api/v1/players/         (list, paginated)
      - GET /api/v1/players/{id}/    (detail; same serializer for now)
    """
    queryset = (
        Player.objects
        .select_related("player_team", "player_type")  # avoid N+1
        # Keep it simple at first: omit `.only(...)` to avoid missing fields during detail
        .order_by("-total_points")
    )
    serializer_class = PlayerListSerializer

    # Filtering / searching / ordering
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class = PlayerFilter

    search_fields = [
        "web_name", "first_name", "second_name",
        "player_team__name", "player_team__short_name",
        "player_type__singular_name_short", "player_type__singular_name",
    ]

    ordering_fields = [
        "total_points", "now_cost", "selected_by_percent",
        "event_points", "form", "value_form", "vapm", "web_name", "id",
    ]
    ordering = ["-total_points"]


class DefenceViewSet(ReadOnlyModelViewSet):
    queryset = (
        Player.objects
        .filter(element_type__in=[1, 2])           # GK + DEF
        .select_related("player_team", "player_type")
        .order_by("-clean_sheets")
    )
    serializer_class = PlayerDefenceSerializer

    # Use the same backends as Players
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]

    # Optional – add search like Players if you want
    search_fields = [
        "web_name", "first_name", "second_name",
        "player_team__name", "player_team__short_name",
        "player_type__singular_name_short", "player_type__singular_name",
    ]

    # Only allow ordering by these fields
    ordering_fields = [
        "clean_sheets","goals_conceded","starts","minutes",
        "clean_sheets_per_90","goals_conceded_per_90","total_points","form"
    ]
    ordering = ["-clean_sheets", "-total_points", "now_cost"]  # default