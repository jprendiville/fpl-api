# players/api/v1/serializers.py
from rest_framework import serializers
from players.models import Player, ElementType
from teams.api.v1.serializers import TeamMiniSerializer


class ElementTypeMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElementType
        fields = (
            "id",
            "singular_name_short",  # e.g., GKP/DEF/MID/FWD
            "plural_name_short",    # e.g., GKs/DEFs/MIDs/FWDs
            "singular_name",        # e.g., Goalkeeper
            "plural_name",          # e.g., Goalkeepers
        )
        read_only_fields = fields


class PlayerListSerializer(serializers.ModelSerializer):
    team = TeamMiniSerializer(source="player_team", read_only=True)
    type = ElementTypeMiniSerializer(source="player_type", read_only=True)

    class Meta:
        model = Player
        fields = (
            "id", "web_name", "status",
            "now_cost", "total_points",
            "selected_by_percent", "event_points",
            "form", "value_form", "vapm",
            "team",  # {id,name,short_name,code}
            "type",  # {id,name}
        )
        read_only_fields = fields
