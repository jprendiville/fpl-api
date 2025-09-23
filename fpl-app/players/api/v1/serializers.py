# players/api/v1/serializers.py
from rest_framework import serializers

from common.utils import get_next_gameweek, get_next_n_games_fdr
from fpl.properties.properties import get_properties
from players.models import Player, ElementType
from teams.api.v1.serializers import TeamMiniSerializer

properties = get_properties()

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
    next_games = serializers.SerializerMethodField()

    class Meta:
        model = Player
        exclude = ("player_team", "player_type")

    def get_next_games(self, obj):
        next_gameweek = get_next_gameweek()
        return get_next_n_games_fdr(
            obj.player_team,
            next_gameweek,
            properties.number_of_gameweeks,
        )


class PlayerDefenceSerializer(serializers.ModelSerializer):
    # replace raw FKs with nested
    team = TeamMiniSerializer(source="player_team", read_only=True)
    type = ElementTypeMiniSerializer(source="player_type", read_only=True)
    next_games = serializers.SerializerMethodField()

    class Meta:
        model = Player
        # include all model fields except the FK sources (we expose them as team/type above)
        exclude = ("player_team", "player_type")

    def get_next_games(self, obj):
        next_gameweek = get_next_gameweek()
        return get_next_n_games_fdr(
            obj.player_team,
            next_gameweek,
            properties.number_of_gameweeks,
        )

class ElementTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElementType
        fields = "__all__"

# players/serializers.py
from rest_framework import serializers
from players.models.player_history import PlayerHistory  # adjust import to your layout

class PlayerHistorySerializer(serializers.ModelSerializer):
    opponent_short_name = serializers.CharField(source="opponent.short_name", read_only=True)
    opponent_name = serializers.CharField(source="opponent.name", read_only=True)
    home_away = serializers.SerializerMethodField()

    class Meta:
        model = PlayerHistory
        fields = '__all__'

    def get_home_away(self, obj: "PlayerHistory") -> str:
        return 'H' if obj.was_home else 'A'
