from rest_framework import serializers

from players.models import PlayerStatus


class PlayerStatusListSerializer(serializers.ListSerializer):
    def update(self, queryset, validated_data):
        # Map existing objects by their primary key (status)
        status_map = {obj.status: obj for obj in queryset}

        updated_objects = []

        for item in validated_data:
            status = item.get("status")
            obj = status_map.get(status)

            if obj is None:
                continue  # or raise an error if you want strictness

            for attr, value in item.items():
                setattr(obj, attr, value)

            obj.save()
            updated_objects.append(obj)

        return updated_objects


class PlayerStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerStatus
        fields = ["status", "description", "can_play", "colour", "last_updated"]
        read_only_fields = ["last_updated"]
        list_serializer_class = PlayerStatusListSerializer
