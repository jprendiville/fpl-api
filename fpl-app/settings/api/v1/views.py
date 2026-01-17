from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from players.models import PlayerStatus
from settings.api.v1.serializers import PlayerStatusSerializer


class PlayerStatusSettingsView(APIView):
    serializer_class = PlayerStatusSerializer

    def get(self, request):
        qs = PlayerStatus.objects.all().order_by("status")
        serializer = PlayerStatusSerializer(qs, many=True)
        return Response(serializer.data)

    def put(self, request):
        """
        Accepts a list of objects:
        [
            { "status": "a", "description": "Available", "can_play": true },
            { "status": "s", "description": "Suspended", "can_play": false }
        ]
        """
        qs = PlayerStatus.objects.all().order_by("status")

        serializer = PlayerStatusSerializer(
            instance=qs,
            data=request.data,
            many=True,
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)