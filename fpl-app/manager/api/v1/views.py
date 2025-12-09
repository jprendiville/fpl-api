# views.py
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, \
    extend_schema
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status

from common.api.v1.views import properties
from common.utils import get_current_gameweek, get_last_completed_gameweek
from fpl.dataloader.load.load_managers import load_manager
from .serializers import ManagerSerializer  # your serializer for the Manager class

class ManagersViewSet(ViewSet):
    """
    GET /api/v1/managers/?ids=123,456
    Returns:
      { "results": [ { ...manager payload... }, ... ] }
    """
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="ids",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Comma-separated manager IDs, e.g. `1162054`",
                examples=[OpenApiExample("Manager Id(s)", value="1162054"),],
            )
        ],
        # optional but nicer docs if you specify a response serializer (see below)
        responses={200: OpenApiTypes.OBJECT},
    )
    def list(self, request):
        ids_param = request.query_params.get("ids", "").strip()
        if not ids_param:
            # Could return 400 if you prefer, but empty works fine:
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
