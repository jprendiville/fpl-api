import logging

from django.db.models import Max
from rest_framework import filters as drf_filters, viewsets
from django_filters.rest_framework import DjangoFilterBackend, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from common.models.event import Event
from common.utils import get_current_gameweek
from fpl.properties.properties import get_properties
from players.models import ElementType, Player, PlayerHistory, PlayerPrediction
from .serializers import ElementTypeSerializer, PlayerDefenceSerializer, \
    PlayerHistorySerializer, PlayerListSerializer, \
    PlayerPredictionHistorySerializer, PlayerPredictionSerializer
from .filters import PlayerFilter
from ...filters import PredictionsFilter

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

properties = get_properties()

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

class PlayerHistoryViewSet(ReadOnlyModelViewSet):
    serializer_class = PlayerHistorySerializer
    pagination_class = None  # modal wants full season in one go
    filter_backends = [DjangoFilterBackend, drf_filters.OrderingFilter]
    ordering_fields = ["round", "kickoff_time"]

    def get_queryset(self):
        qs = (
            PlayerHistory.objects
            .select_related("opponent", "player")
            .order_by("-round", "kickoff_time")
        )
        player_id = self.kwargs.get("player_id")
        if player_id is not None:
            qs = qs.filter(player_id=player_id)
        p = self.request.query_params.get("player")
        if p:
            qs = qs.filter(player_id=p)
        return qs


class PredictionsViewSet(ReadOnlyModelViewSet):
    """
    Endpoints:
      - GET /api/v1/predictions/         (list, paginated)
      - GET /api/v1/predictions/{id}/    (detail)
    """

    serializer_class = PlayerPredictionSerializer

    # Filtering / searching / ordering
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class = PredictionsFilter

    search_fields = [
        "player__web_name",
        "player__first_name",
        "player__second_name",
        "player__player_team__name",
        "player__player_team__short_name",
    ]

    ordering_fields = [
        "prediction",
        "player__web_name",
        "player__id",
    ]
    ordering = ["-prediction"]

    def get_queryset(self):
        """
        Equivalent to the queryset in your PlayerViewSet,
        but for PlayerPrediction instead of Player.
        """
        latest_gw = (
            PlayerPrediction.objects
            .aggregate(Max("gameweek_id"))
            .get("gameweek_id__max")
        )

        return (
            PlayerPrediction.objects
            .select_related("player", "player__player_team", "player__player_type")
            .filter(gameweek_id=latest_gw)
            .order_by("-prediction")
        )


class PlayerPredictionHistoryViewSet(ReadOnlyModelViewSet):
    serializer_class = PlayerPredictionHistorySerializer
    pagination_class = None  # modal wants full season in one go
    filter_backends = [DjangoFilterBackend, drf_filters.OrderingFilter]
    ordering_fields = ["round", "kickoff_time"]

    def get_queryset(self):
        qs = (
            PlayerPrediction.objects
            .select_related("opponent", "player")
            .order_by("-gameweek")
        )
        player_id = self.kwargs.get("player_id")
        if player_id is not None:
            qs = qs.filter(player_id=player_id)
        p = self.request.query_params.get("player")
        if p:
            qs = qs.filter(player_id=p)
        return qs


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
    filterset_class = PlayerFilter

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


class TransfersInViewSet(ReadOnlyModelViewSet):
    serializer_class = PlayerListSerializer

    def get_queryset(self):
        qs = Player.objects.order_by("-transfers_in_event")
        return PlayerFilter(self.request.GET, queryset=qs).qs


class TransfersOutViewSet(ReadOnlyModelViewSet):
    serializer_class = PlayerListSerializer

    def get_queryset(self):
        qs = Player.objects.order_by("-transfers_out_event")
        return PlayerFilter(self.request.GET, queryset=qs).qs


class ElementTypeViewSet(ReadOnlyModelViewSet):
    queryset = (
        ElementType.objects
        .order_by("id")
    )
    serializer_class = ElementTypeSerializer
    filter_backends = []
    pagination_class = None
