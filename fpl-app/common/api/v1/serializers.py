# players/api/v1/serializers.py
from rest_framework import serializers

from common.models.event import Event


class EventMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event


