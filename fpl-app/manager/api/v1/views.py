# views.py
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample, OpenApiParameter, extend_schema
)
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from common.api.v1.views import properties
from common.utils import get_current_gameweek, get_last_completed_gameweek
from fpl.dataloader.load.load_managers import load_manager

from .serializers import (
    ManagerSerializer,
    ManagerLeaguesSerializer,   # <-- add this import
)

class ManagersViewSet(ViewSet):
    """
    GET /api/v1/managers/?ids=123,456
    GET /api/v1/managers/leagues/?ids=123,456
    GET /api/v1/managers/{id}/leagues/
    """

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="ids",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Comma-separated manager IDs, e.g. `1162054`",
                examples=[OpenApiExample("Manager Id(s)", value="1162054")],
            )
        ],
        responses={200: OpenApiTypes.OBJECT},
    )
    def list(self, request):
        ids_param = request.query_params.get("ids", "").strip()
        if not ids_param:
            return Response({"results": []})

        try:
            ids = [int(x) for x in ids_param.split(",") if x.strip()]
        except ValueError:
            return Response(
                {"detail": "ids must be integers, comma-separated"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        current_gw = get_current_gameweek()
        last_completed_gw = get_last_completed_gameweek()

        results = []
        for manager_id in ids:
            mgr = load_manager(
                manager_id,
                0,
                properties.number_of_gameweeks,
                current_gw,
                last_completed_gw,
            )
            results.append(ManagerSerializer(mgr).data)

        return Response({"results": results})

    # -------- NEW: leagues (collection) --------
    @extend_schema(
        operation_id="managers_leagues_list",
        parameters=[
            OpenApiParameter(
                name="ids",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Comma-separated manager IDs, e.g. `1162054`",
                examples=[OpenApiExample("Manager Id(s)", value="1162054,123456")],
            )
        ],
        responses={200: OpenApiTypes.OBJECT},
    )
    @action(detail=False, methods=["get"], url_path="leagues")
    def leagues(self, request):
        """
        GET /api/v1/managers/leagues/?ids=123,456
        Returns { "results": [ { information, manager_team, classic_leagues }, ... ] }
        """
        ids_param = request.query_params.get("ids", "").strip()
        if not ids_param:
            return Response({"results": []})

        try:
            ids = [int(x) for x in ids_param.split(",") if x.strip()]
        except ValueError:
            return Response(
                {"detail": "ids must be integers, comma-separated"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        current_gw = get_current_gameweek()
        last_completed_gw = get_last_completed_gameweek()

        def to_leagues_payload(mgr):
            # Only surface the bits the leagues page needs
            payload = {
                "information": getattr(mgr, "information", None),
                "manager_team": getattr(mgr, "manager_team", None),
                "classic_leagues": getattr(mgr, "classic_leagues", []) or [],
            }
            return ManagerLeaguesSerializer(payload).data

        results = []
        for manager_id in ids:
            mgr = load_manager(
                manager_id,
                0,
                properties.number_of_gameweeks,
                current_gw,
                last_completed_gw,
            )
            results.append(to_leagues_payload(mgr))

        return Response({"results": results})

    # -------- NEW: leagues (per-manager) --------
    @extend_schema(
        operation_id="manager_leagues_detail",
        responses={200: ManagerLeaguesSerializer},
    )
    @action(detail=True, methods=["get"], url_path="leagues")
    def leagues_for_manager(self, request, pk: str = ""):
        """
        GET /api/v1/managers/{id}/leagues/
        Returns { information, manager_team, classic_leagues }
        """
        try:
            manager_id = int(pk)
        except ValueError:
            return Response(
                {"detail": "Invalid manager id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        current_gw = get_current_gameweek()
        last_completed_gw = get_last_completed_gameweek()

        mgr = load_manager(
            manager_id,
            0,
            properties.number_of_gameweeks,
            current_gw,
            last_completed_gw,
        )
        payload = {
            "information": getattr(mgr, "information", None),
            "manager_team": getattr(mgr, "manager_team", None),
            "classic_leagues": getattr(mgr, "classic_leagues", []) or [],
        }
        return Response(ManagerLeaguesSerializer(payload).data)
