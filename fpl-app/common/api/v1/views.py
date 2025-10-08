from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ReadOnlyModelViewSet

from common.api.v1.serializers import EventSerializer
from common.models.event import Event
from common.utils import get_next_gameweek
from fpl.properties.properties import get_properties

properties = get_properties()

class EventViewSet(ReadOnlyModelViewSet):
    """
    Endpoints:
      - GET /api/v1/events/           (list, paginated)
      - GET /api/v1/events/{id}/      (detail)
      - GET /api/v1/events/upcoming/  (custom action: next N gameweeks)
    """
    queryset = Event.objects.all().order_by("id")
    serializer_class = EventSerializer

    @action(detail=False, methods=["get"])
    def upcoming(self, request):
        next_gw = get_next_gameweek()
        qs = (
            Event.objects.filter(id__gte=next_gw.id)
            .order_by("id")[: properties.number_of_gameweeks]
        )
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def finished(self, request):
        qs = (
            Event.objects.filter(finished=True)
            .order_by("-id")
        )
        serializer = self.get_serializer(qs, many=True)
        print(serializer)
        return Response(serializer.data)