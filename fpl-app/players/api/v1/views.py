from rest_framework import viewsets, filters as drf_filters
from django_filters.rest_framework import DjangoFilterBackend
from players.models import Player
from .serializers import PlayerListSerializer
from .filters import PlayerFilter

class PlayerViewSet(viewsets.ReadOnlyModelViewSet):
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
