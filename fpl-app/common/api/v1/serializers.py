# players/api/v1/serializers.py
from rest_framework import serializers

from common.models.event import Event


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ("__all__")
